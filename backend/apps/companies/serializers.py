from rest_framework import serializers
from .models import Company, AnydeskStation, IikoDistribution, City, BusinessType, LicenceType, AnydeskVersion, ServiceType, CompanyService
from apps.common.crypto import encrypt_password, decrypt_password
from .utils import clean_iiko_version, get_distribution_link

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'created_at')


class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ('id', 'name', 'created_at')


class LicenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenceType
        fields = ('id', 'name', 'created_at')


class AnydeskStationSerializer(serializers.ModelSerializer):
    company_place_name = serializers.CharField(source='company.place_name', read_only=True)
    company_city = serializers.CharField(source='company.city', read_only=True)
    company_software_type = serializers.CharField(source='company.software_type', read_only=True, default='IIKO')

    class Meta:
        model = AnydeskStation
        fields = (
            'id', 'company', 'company_place_name', 'company_city', 'company_software_type',
            'description', 'anydesk_id', 'any_pass',
            'created_at', 'updated_at'
        )


class ChainOptionSerializer(serializers.ModelSerializer):
    branches_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ('id', 'place_name', 'city', 'branches_count')

    def get_branches_count(self, obj):
        return obj.branches.filter(status=True).count()


class ServiceTypeSerializer(serializers.ModelSerializer):
    subscriptions_count = serializers.IntegerField(source='subscriptions.count', read_only=True)

    class Meta:
        model = ServiceType
        fields = ('id', 'name', 'code', 'is_its', 'description', 'subscriptions_count', 'created_at')


class CompanyServiceSerializer(serializers.ModelSerializer):
    company_place_name = serializers.CharField(source='company.place_name', read_only=True)
    company_city = serializers.CharField(source='company.city', read_only=True)
    company_node_type = serializers.CharField(source='company.node_type', read_only=True)
    company_branches_count = serializers.SerializerMethodField()
    company_stations_count = serializers.IntegerField(source='company.anydesk_stations.count', read_only=True)
    company_parent_chain_name = serializers.CharField(source='company.parent_chain.place_name', read_only=True, default=None)
    service_code = serializers.CharField(source='service.code', read_only=True)
    is_its = serializers.BooleanField(source='service.is_its', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    start_date = serializers.DateField(required=False, allow_null=True)

    def get_company_branches_count(self, obj):
        if obj.company:
            return obj.company.branches.filter(status=True).count()
        return 0

    class Meta:
        model = CompanyService
        fields = (
            'id', 'company', 'company_place_name', 'company_city', 'company_node_type',
            'company_branches_count', 'company_stations_count', 'company_parent_chain_name',
            'service', 'service_name', 'service_code', 'is_its',
            'period_type', 'pricing_type', 'cost_per_rms', 'quantity', 'total_cost',
            'start_date', 'expires_at', 'days_remaining',
            'status', 'comment', 'created_at', 'updated_at'
        )

    def to_internal_value(self, data):
        # Prevent validation error {"start_date":["Неправильный формат date..."]} when start_date is empty string or full ISO string
        if 'start_date' in data:
            val = data.get('start_date')
            if val == '' or val is None:
                data = data.copy() if hasattr(data, 'copy') else dict(data)
                data['start_date'] = None
            elif isinstance(val, str) and 'T' in val:
                data = data.copy() if hasattr(data, 'copy') else dict(data)
                data['start_date'] = val.split('T')[0]
        return super().to_internal_value(data)

    def get_days_remaining(self, obj):
        if not obj.expires_at:
            return None
        from datetime import date
        today = date.today()
        return (obj.expires_at - today).days

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            role = getattr(request.user, 'role', '')
            if role not in ['SUPERADMIN', 'MANAGER']:
                ret['cost_per_rms'] = None
                ret['total_cost'] = None
        return ret


class CompanyWebkassaMixin:
    def _get_active_cash_registers(self, obj):
        if hasattr(obj, '_cached_active_cash_registers'):
            return obj._cached_active_cash_registers
        try:
            regs = [r for r in obj.cash_registers.all() if getattr(r, 'is_active', True)]
        except Exception:
            regs = []
        obj._cached_active_cash_registers = regs
        return regs

    def get_webkassa_count(self, obj):
        return len(self._get_active_cash_registers(obj))

    def get_webkassa_expires_at(self, obj):
        regs = [r for r in self._get_active_cash_registers(obj) if r.expires_at]
        if not regs:
            return None
        earliest = min(regs, key=lambda r: r.expires_at)
        return earliest.expires_at

    def get_webkassa_days_remaining(self, obj):
        regs = [r for r in self._get_active_cash_registers(obj) if r.expires_at]
        if not regs:
            return None
        earliest = min(regs, key=lambda r: r.expires_at)
        from datetime import date
        return (earliest.expires_at - date.today()).days

    def get_webkassa_registers(self, obj):
        regs = self._get_active_cash_registers(obj)
        if not regs:
            return []
        from datetime import date
        today = date.today()
        return [
            {
                'id': r.id,
                'name': r.name,
                'serial_number': r.serial_number,
                'status': r.status,
                'ofd': r.ofd,
                'expires_at': r.expires_at.isoformat() if r.expires_at else None,
                'days_remaining': (r.expires_at - today).days if r.expires_at else None,
            }
            for r in regs
        ]


class CompanyListSerializer(CompanyWebkassaMixin, serializers.ModelSerializer):
    stations_count = serializers.IntegerField(source='anydesk_stations.count', read_only=True)
    anydesk_stations = AnydeskStationSerializer(many=True, read_only=True)
    branches_count = serializers.SerializerMethodField()
    parent_chain_name = serializers.CharField(source='parent_chain.place_name', read_only=True, default=None)
    system_admin_password = serializers.SerializerMethodField()
    distribution_link = serializers.SerializerMethodField()
    its_days_remaining = serializers.SerializerMethodField()
    webkassa_count = serializers.SerializerMethodField()
    webkassa_days_remaining = serializers.SerializerMethodField()
    webkassa_expires_at = serializers.SerializerMethodField()
    webkassa_registers = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    def get_branches_count(self, obj):
        return obj.branches.filter(status=True).count()

    class Meta:
        model = Company
        fields = (
            'id', 'software_type', 'node_type', 'parent_chain', 'parent_chain_name',
            'branches_count', 'place_name', 'company_name', 'bin', 'cabinet_name',
            'crm_id', 'uid', 'system_admin_name', 'system_admin_password',
            'business_type', 'licence_type', 'iiko_version',
            'server_name', 'port_number', 'city', 'status',
            'iiko_rosta', 'sort_number', 'no_ip', 'helpdesk_its', 'its_expires_at', 'its_days_remaining', 'its_cost', 'iiko_web_address',
            'webkassa_count', 'webkassa_days_remaining', 'webkassa_expires_at', 'webkassa_registers',
            'license_data', 'license_updated_at', 'last_license_error',
            'stations_count', 'anydesk_stations', 'distribution_link', 'created_at', 'updated_at', 'updated_by_name'
        )
        read_only_fields = ('its_cost', 'its_days_remaining', 'webkassa_count', 'webkassa_days_remaining', 'webkassa_expires_at', 'webkassa_registers')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Services are provided only to active establishments
        if not instance.status:
            ret['helpdesk_its'] = 'Нет'
            ret['its_expires_at'] = None
            ret['its_cost'] = None
            ret['its_days_remaining'] = None
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            role = getattr(request.user, 'role', '')
            if role not in ['SUPERADMIN', 'MANAGER']:
                ret['its_cost'] = None
        return ret

    def get_system_admin_password(self, obj):
        return obj.get_password()

    def get_distribution_link(self, obj):
        return get_distribution_link(obj.iiko_version, obj.node_type)

    def get_its_days_remaining(self, obj):
        if not obj.its_expires_at:
            return None
        from datetime import date
        today = date.today()
        return (obj.its_expires_at - today).days

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return None
        return obj.updated_by.full_name or obj.updated_by.username


class CompanyDetailSerializer(CompanyWebkassaMixin, serializers.ModelSerializer):
    anydesk_stations = AnydeskStationSerializer(many=True, read_only=True)
    company_services = CompanyServiceSerializer(many=True, read_only=True)
    branches_count = serializers.SerializerMethodField()
    parent_chain_name = serializers.CharField(source='parent_chain.place_name', read_only=True, default=None)
    system_admin_password = serializers.CharField(required=False, allow_blank=True, write_only=False)
    distribution_link = serializers.SerializerMethodField()
    its_days_remaining = serializers.SerializerMethodField()
    webkassa_count = serializers.SerializerMethodField()
    webkassa_days_remaining = serializers.SerializerMethodField()
    webkassa_expires_at = serializers.SerializerMethodField()
    webkassa_registers = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    its_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True, read_only=True)

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        data.pop('its_cost', None)
        return super().to_internal_value(data)

    def get_branches_count(self, obj):
        return obj.branches.filter(status=True).count()

    class Meta:
        model = Company
        fields = (
            'id', 'software_type', 'node_type', 'parent_chain', 'parent_chain_name',
            'branches_count', 'place_name', 'company_name', 'bin', 'cabinet_name',
            'crm_id', 'uid', 'system_admin_name', 'system_admin_password',
            'business_type', 'licence_type', 'iiko_version',
            'server_name', 'port_number', 'image_link', 'no_ip',
            'iiko_rosta', 'sort_number', 'helpdesk_its', 'its_expires_at', 'its_days_remaining', 'its_cost', 'city',
            'webkassa_count', 'webkassa_days_remaining', 'webkassa_expires_at', 'webkassa_registers',
            'status', 'iiko_web_address', 'license_data', 'license_updated_at', 'last_license_error', 'anydesk_stations', 'company_services',
            'distribution_link', 'created_at', 'updated_at', 'updated_by_name'
        )
        read_only_fields = ('its_cost', 'its_days_remaining', 'webkassa_count', 'webkassa_days_remaining', 'webkassa_expires_at', 'webkassa_registers')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Services are provided only to active establishments
        if not instance.status:
            ret['helpdesk_its'] = 'Нет'
            ret['its_expires_at'] = None
            ret['its_cost'] = None
            ret['its_days_remaining'] = None
        ret['system_admin_password'] = instance.get_password()
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            role = getattr(request.user, 'role', '')
            if role not in ['SUPERADMIN', 'MANAGER']:
                ret['its_cost'] = None
        return ret

    def get_distribution_link(self, obj):
        return get_distribution_link(obj.iiko_version, obj.node_type)

    def get_its_days_remaining(self, obj):
        if not obj.its_expires_at:
            return None
        from datetime import date
        today = date.today()
        return (obj.its_expires_at - today).days

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return None
        return obj.updated_by.full_name or obj.updated_by.username

    def create(self, validated_data):
        password = validated_data.pop('system_admin_password', None)
        # If node_type is CHAIN, parent_chain should be None
        if validated_data.get('node_type') == Company.NodeType.CHAIN:
            validated_data['parent_chain'] = None

        company = super().create(validated_data)
        if company.node_type == Company.NodeType.CHAIN and not company.sort_number:
            company.sort_number = company.id
            company.save(update_fields=['sort_number'])

        if password is not None:
            company.set_password(password)
            company.save(update_fields=['system_admin_password_enc'])

        # Ensure city, business_type, licence_type exist in directory tables
        if company.city:
            City.objects.get_or_create(name=company.city.strip())
        if company.business_type:
            BusinessType.objects.get_or_create(name=company.business_type.strip())
        if company.licence_type:
            LicenceType.objects.get_or_create(name=company.licence_type.strip())

        return company

    def update(self, instance, validated_data):
        password = validated_data.pop('system_admin_password', None)
        if validated_data.get('node_type') == Company.NodeType.CHAIN:
            validated_data['parent_chain'] = None

        company = super().update(instance, validated_data)
        if password is not None:
            company.set_password(password)
            company.save(update_fields=['system_admin_password_enc'])

        # Ensure city, business_type, licence_type exist in directory tables
        if company.city:
            City.objects.get_or_create(name=company.city.strip())
        if company.business_type:
            BusinessType.objects.get_or_create(name=company.business_type.strip())
        if company.licence_type:
            LicenceType.objects.get_or_create(name=company.licence_type.strip())

        return company

    def validate_iiko_version(self, value):
        return clean_iiko_version(value)


class IikoDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IikoDistribution
        fields = ('id', 'iiko_version', 'type', 'link_ya', 'created_at')

    def validate_iiko_version(self, value):
        return clean_iiko_version(value)


class AnydeskVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnydeskVersion
        fields = ('id', 'name', 'exe_path', 'is_sandbox', 'sandbox_params', 'is_default', 'order', 'created_at')
