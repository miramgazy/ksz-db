from datetime import date
from rest_framework import serializers
from .models import WebkassaCTO, WebkassaCashRegister
from apps.companies.models import Company


class WebkassaCTOSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebkassaCTO
        fields = ('id', 'name', 'created_at')


class WebkassaCashRegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True, default='')
    company_place_name = serializers.CharField(source='company.place_name', read_only=True, default='')
    company_city = serializers.CharField(source='company.city', read_only=True, default='')
    company_software_type = serializers.CharField(source='company.software_type', read_only=True, default='')
    company_node_type = serializers.CharField(source='company.node_type', read_only=True, default='')
    company_bin = serializers.CharField(source='company.bin', read_only=True, default='')
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = WebkassaCashRegister
        fields = (
            'id', 'is_active', 'cto', 'name', 'serial_number', 'status', 'ofd',
            'bin_iin', 'organization', 'expires_at', 'company',
            'company_name', 'company_place_name', 'company_city',
            'company_software_type', 'company_node_type', 'company_bin',
            'auto_matched', 'comment', 'days_remaining',
            'created_at', 'updated_at'
        )

    def get_days_remaining(self, obj):
        if not obj.expires_at:
            return None
        return (obj.expires_at - date.today()).days
