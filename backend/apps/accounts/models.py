from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'Суперадминистратор'
        MANAGER = 'MANAGER', 'Менеджер'
        VIEWER = 'VIEWER', 'Наблюдатель'

    class RegistrationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает одобрения'
        ACTIVE = 'ACTIVE', 'Активирован'
        REJECTED = 'REJECTED', 'Отклонен'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.VIEWER,
        verbose_name='Роль'
    )
    registration_status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
        verbose_name='Статус регистрации'
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Полное имя (ФИО)'
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Телефон'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        name = self.full_name or self.username
        return f"{name} ({self.get_role_display()})"
