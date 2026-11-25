from django.contrib import admin
from .models import WebkassaCTO, WebkassaCashRegister


@admin.register(WebkassaCTO)
class WebkassaCTOAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(WebkassaCashRegister)
class WebkassaCashRegisterAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'is_active', 'name', 'cto', 'status', 'expires_at', 'company', 'auto_matched')
    list_filter = ('is_active', 'cto', 'status', 'auto_matched')
    search_fields = ('serial_number', 'name', 'bin_iin', 'organization', 'company__place_name')
