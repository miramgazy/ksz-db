from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import (
    update_agent_online,
    get_agent_online,
    poll_agent_task,
    submit_agent_result,
    send_task_and_wait,
)

class CompanionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        online, meta = get_agent_online(request.user.id)
        return Response({
            "online": online,
            "data": meta or None,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "full_name": request.user.full_name or request.user.username,
            }
        })


class CompanionLaunchBackofficeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = send_task_and_wait(request.user.id, "launch_backoffice", request.data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionLaunchLicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = send_task_and_wait(request.user.id, "launch_license", request.data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionInsertClearbatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = send_task_and_wait(request.user.id, "insert_clearbat", request.data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionLaunchAnydeskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = send_task_and_wait(request.user.id, "launch_anydesk", request.data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionAgentPollView(APIView):
    """
    Endpoint called in an infinite polling loop by the engineer's local ksz_helper.py.
    Registers presence and holds connection until a command is queued or timeout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        meta = dict(request.data)
        meta["user_id"] = request.user.id
        meta["username"] = request.user.username
        meta["full_name"] = request.user.full_name or request.user.username

        update_agent_online(request.user.id, meta)

        task = poll_agent_task(request.user.id, timeout=25)
        if task:
            return Response({"status": "command", "task": task})
        return Response({"status": "idle"})


class CompanionAgentResultView(APIView):
    """
    Endpoint called by ksz_helper.py to deliver execution result back to the server.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get("task_id")
        result = request.data.get("result")
        if result is None:
            result = request.data

        if not task_id:
            return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        submit_agent_result(task_id, result)
        return Response({"status": "ok"})
