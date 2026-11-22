import os
import json
import uuid
import redis
from django.conf import settings

def get_redis_client():
    host = getattr(settings, 'REDIS_HOST', os.getenv('REDIS_HOST', 'redis'))
    port = int(getattr(settings, 'REDIS_PORT', os.getenv('REDIS_PORT', 6379)))
    return redis.Redis(host=host, port=port, db=0, decode_responses=True)

def update_agent_online(user_id: int, metadata: dict):
    """Refreshes the online status of a user's agent in Redis with 45s TTL."""
    r = get_redis_client()
    key = f"companion:online:{user_id}"
    r.set(key, json.dumps(metadata), ex=45)

def get_agent_online(user_id: int):
    """Checks whether the agent for the given user is currently online."""
    r = get_redis_client()
    key = f"companion:online:{user_id}"
    raw = r.get(key)
    if raw:
        try:
            return True, json.loads(raw)
        except Exception:
            return True, {}
    return False, None

def poll_agent_task(user_id: int, timeout: int = 25):
    """Blocks waiting for a task in the user's queue."""
    r = get_redis_client()
    queue_key = f"companion:queue:{user_id}"
    item = r.blpop(queue_key, timeout=timeout)
    if item and len(item) == 2:
        try:
            return json.loads(item[1])
        except Exception:
            return None
    return None

def submit_agent_result(task_id: str, result: dict):
    """Stores the execution result from the agent for the waiting web request."""
    r = get_redis_client()
    result_key = f"companion:result:{task_id}"
    r.rpush(result_key, json.dumps(result))
    r.expire(result_key, 30)

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
    res = r.blpop(result_key, timeout=timeout)
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
