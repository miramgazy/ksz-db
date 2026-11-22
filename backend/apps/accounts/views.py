from rest_framework import generics, viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.common.permissions import IsSuperAdmin
from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserApprovalSerializer,
    CustomTokenObtainPairSerializer,
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Заявка на регистрацию успешно отправлена! Ваш доступ проверяется администратором.",
                "user": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    User management ViewSet — restricted to SUPERADMIN only.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsSuperAdmin,)
    filterset_fields = ('registration_status', 'role', 'is_active')
    search_fields = ('username', 'email', 'full_name', 'phone')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        serializer = UserApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data.get('role')
        if new_role:
            user.role = new_role

        user.is_active = True
        user.registration_status = User.RegistrationStatus.ACTIVE
        user.save()

        return Response({
            "message": f"Пользователь {user.username} успешно активирован с ролью {user.get_role_display()}.",
            "user": UserSerializer(user).data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.registration_status = User.RegistrationStatus.REJECTED
        user.save()

        return Response({
            "message": f"Заявка пользователя {user.username} отклонена.",
            "user": UserSerializer(user).data
        })
