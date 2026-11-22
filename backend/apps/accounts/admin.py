from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'registration_status', 'is_active', 'date_joined')
    list_filter = ('role', 'registration_status', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'full_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Роли и Доступ', {
            'fields': ('role', 'registration_status', 'full_name', 'phone')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Роли и Доступ', {
            'fields': ('role', 'registration_status', 'full_name', 'phone')
        }),
    )

    actions = ['approve_users', 'reject_users']

    @admin.action(description='Активировать выбранных пользователей')
    def approve_users(self, request, queryset):
        queryset.update(is_active=True, registration_status=User.RegistrationStatus.ACTIVE)

    @admin.action(description='Отклонить выбранных пользователей')
    def reject_users(self, request, queryset):
        queryset.update(is_active=False, registration_status=User.RegistrationStatus.REJECTED)
