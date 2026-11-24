import os
import json
import uuid
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

def get_redis_client():
    host = getattr(settings, 'REDIS_HOST', os.getenv('REDIS_HOST', 'redis'))
    port = int(getattr(settings, 'REDIS_PORT', os.getenv('REDIS_PORT', 6379)))
    return redis.Redis(
        host=host,
        port=port,
        db=0,
        decode_responses=True,
        socket_timeout=None,  # Do not drop socket during long BLPOP blocking waits
        socket_connect_timeout=5,
        health_check_interval=30
    )

def update_agent_online(user_id: int, metadata: dict):
    """Refreshes the online status of a user's agent in Redis with 45s TTL."""
    try:
        r = get_redis_client()
        key = f"companion:online:{user_id}"
        r.set(key, json.dumps(metadata), ex=45)
    except Exception as e:
        logger.warning(f"Failed to update agent online status: {e}")

def get_agent_online(user_id: int):
    """Checks whether the agent for the given user is currently online."""
    try:
        r = get_redis_client()
        key = f"companion:online:{user_id}"
        raw = r.get(key)
        if raw:
            try:
                return True, json.loads(raw)
            except Exception:
                return True, {}
    except Exception as e:
        logger.warning(f"Failed to get agent online status: {e}")
    return False, None

def poll_agent_task(user_id: int, timeout: int = 20):
    """Blocks waiting for a task in the user's queue."""
    r = get_redis_client()
    queue_key = f"companion:queue:{user_id}"
    try:
        item = r.blpop(queue_key, timeout=timeout)
        if item and len(item) == 2:
            try:
                return json.loads(item[1])
            except Exception:
                return None
    except (redis.exceptions.TimeoutError, TimeoutError):
        # Normal timeout when no command arrived in the poll interval
        return None
    except Exception as e:
        logger.warning(f"Error in poll_agent_task: {e}")
        return None
    return None

def submit_agent_result(task_id: str, result: dict):
    """Stores the execution result from the agent for the waiting web request."""
    try:
        r = get_redis_client()
        result_key = f"companion:result:{task_id}"
        r.rpush(result_key, json.dumps(result))
        r.expire(result_key, 60)
        set_task_status(task_id, result, ttl=120)
    except Exception as e:
        logger.warning(f"Failed to submit agent result: {e}")

def set_task_status(task_id: str, status_data: dict, ttl: int = 120):
    """Saves asynchronous task status in Redis for polling by frontend."""
    try:
        r = get_redis_client()
        key = f"companion:task_status:{task_id}"
        r.set(key, json.dumps(status_data), ex=ttl)
    except Exception as e:
        logger.warning(f"Failed to set task status: {e}")

def get_task_status(task_id: str) -> dict:
    """Retrieves asynchronous task status from Redis."""
    try:
        r = get_redis_client()
        key = f"companion:task_status:{task_id}"
        raw = r.get(key)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                return {"status": "unknown"}
    except Exception as e:
        logger.warning(f"Failed to get task status: {e}")
    return {"status": "pending"}

def send_task_async(user_id: int, action: str, payload: dict):
    """
    Pushes an action to the user's agent queue asynchronously (fire-and-forget).
    Returns immediately without blocking the web request or Django worker thread.
    Ideal for launching desktop apps (ClearBat, AnyDesk) where result is handled locally.
    """
    online, meta = get_agent_online(user_id)
    if not online:
        return {
            "success": False,
            "message": "Локальный агент не запущен на вашем рабочем месте. Запустите агент на ПК."
        }

    try:
        r = get_redis_client()
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "action": action,
            "payload": payload,
            "async": True
        }

        queue_key = f"companion:queue:{user_id}"
        r.rpush(queue_key, json.dumps(task_data))
        set_task_status(task_id, {"status": "pending", "action": action, "company_id": payload.get('company_id')}, ttl=120)

        return {
            "success": True,
            "message": "Команда передана локальному агенту.",
            "task_id": task_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка отправки задачи агенту: {str(e)}"
        }

def send_task_and_wait(user_id: int, action: str, payload: dict, timeout: int = 12):
    """
    Pushes an action to the user's agent queue and waits synchronously
    for the agent's response.
    """
    online, meta = get_agent_online(user_id)
    if not online:
        return {
            "success": False,
            "message": "Локальный агент не запущен на вашем рабочем месте. Запустите run_agent.bat."
        }

    try:
        r = get_redis_client()
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "action": action,
            "payload": payload
        }

        queue_key = f"companion:queue:{user_id}"
        result_key = f"companion:result:{task_id}"

        r.rpush(queue_key, json.dumps(task_data))

        # Wait for the agent to complete the task and return result
        try:
            res = r.blpop(result_key, timeout=timeout)
        except (redis.exceptions.TimeoutError, TimeoutError):
            return {
                "success": False,
                "message": "Время ожидания ответа от локального агента истекло."
            }

        if not res or len(res) < 2:
            return {
                "success": False,
                "message": "Время ожидания ответа от локального агента истекло."
            }

        try:
            return json.loads(res[1])
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка обработки ответа агента: {str(e)}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка очереди Redis: {str(e)}"
        }
