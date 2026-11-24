import base64
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
    send_task_async,
)


def ensure_clearbat_base64_password(pwd: str) -> str:
    """
    ClearBat SQLite database (Entities table) strictly requires passwords
    to be encoded in Base64 (as verified in MS Access Form_Company_details).
    """
    if not pwd:
        return ''
    raw = pwd.strip()
    try:
        decoded_bytes = base64.b64decode(raw.encode('ascii'), validate=True)
        if base64.b64encode(decoded_bytes).decode('ascii') == raw:
            decoded_bytes.decode('utf-8')
            return raw
    except Exception:
        pass
    return base64.b64encode(pwd.encode('utf-8')).decode('ascii')

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
        res = send_task_async(request.user.id, "launch_backoffice", request.data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionLaunchLicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        company_id = data.get('company_id')
        if company_id:
            try:
                from apps.companies.models import Company
                comp = Company.objects.get(id=company_id)
                if not data.get('server'):
                    data['server'] = comp.server_name or ''
                if not data.get('port'):
                    data['port'] = comp.port_number or '443'
                if not data.get('login'):
                    data['login'] = comp.system_admin_name or 'iikoadm'
                if not data.get('password'):
                    data['password'] = comp.get_password() or ''
                if not data.get('place_name'):
                    data['place_name'] = comp.place_name
            except Exception:
                pass

        server = (data.get('server') or '').strip()
        if not server:
            return Response(
                {
                    "success": False,
                    "error": "Адрес сервера не указан. Запрос на обновление лицензии не может быть отправлен.",
                    "message": "Адрес сервера не указан. Запрос на обновление лицензии не может быть отправлен."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        res = send_task_async(request.user.id, "launch_license", data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        from .services import get_task_status
        status_data = get_task_status(task_id)
        return Response(status_data)


class CompanionInsertClearbatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        company_id = data.get('company_id')
        if company_id:
            try:
                from apps.companies.models import Company
                comp = Company.objects.get(id=company_id)
                data['name'] = comp.place_name
                data['server'] = comp.server_name or ''
                data['port'] = comp.port_number or '443'
                data['login'] = comp.system_admin_name or 'iikoadm'
                plain_pass = comp.get_password() or ''
                data['password'] = base64.b64encode(plain_pass.encode('utf-8')).decode('ascii') if plain_pass else ''
            except Exception:
                pass
        else:
            pwd = data.get('password', '')
            if pwd:
                data['password'] = ensure_clearbat_base64_password(pwd)

        res = send_task_and_wait(request.user.id, "insert_clearbat", data)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class CompanionLaunchAnydeskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = send_task_async(request.user.id, "launch_anydesk", request.data)
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
