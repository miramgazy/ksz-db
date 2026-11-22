from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'phone', 'role', 'password', 'password_confirm')

    def validate_role(self, value):
        # Disallow self-registering as SUPERADMIN
        if value not in [User.Roles.MANAGER, User.Roles.VIEWER]:
            return User.Roles.VIEWER
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # New users are inactive until approved by Superadmin
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            full_name=validated_data.get('full_name', ''),
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Roles.VIEWER),
            is_active=False,
            registration_status=User.RegistrationStatus.PENDING
        )
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    registration_status_display = serializers.CharField(source='get_registration_status_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'full_name', 'phone',
            'role', 'role_display',
            'registration_status', 'registration_status_display',
            'is_active', 'date_joined', 'updated_at'
        )
        read_only_fields = ('id', 'date_joined', 'updated_at')


class UserApprovalSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Roles.choices, required=False)
    comment = serializers.CharField(required=False, allow_blank=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer with clear error messages for pending/rejected accounts.
    """
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        # Find user by username or email
        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()

        if user and user.check_password(password):
            if user.registration_status == User.RegistrationStatus.PENDING or not user.is_active:
                raise serializers.ValidationError(
                    {"detail": "Ваша учетная запись ожидает одобрения суперадминистратором. Доступ еще не активирован."}
                )
            if user.registration_status == User.RegistrationStatus.REJECTED:
                raise serializers.ValidationError(
                    {"detail": "Ваша учетная запись была отклонена администратором."}
                )

        data = super().validate(attrs)
        
        # Include user profile in login response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'email': self.user.email,
            'role': self.user.role,
            'role_display': self.user.get_role_display(),
        }
        return data
