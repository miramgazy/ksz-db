import base64
from django.utils import timezone
from django.db.models import F, Value, IntegerField, Case, When
from django.db.models.functions import Coalesce
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import ReadOnlyForViewer
from .models import Company, AnydeskStation, IikoDistribution, City, BusinessType, LicenceType, AnydeskVersion, ServiceType, CompanyService
from .utils import version_sort_key, clean_iiko_version, sync_iiko_version_with_distributions
from .serializers import (
    CompanyListSerializer,
    CompanyDetailSerializer,
    AnydeskStationSerializer,
    IikoDistributionSerializer,
    CitySerializer,
    BusinessTypeSerializer,
    LicenceTypeSerializer,
    ChainOptionSerializer,
    AnydeskVersionSerializer,
    ServiceTypeSerializer,
    CompanyServiceSerializer,
)

class CityViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Cities directory.
    """
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer
    permission_classes = (ReadOnlyForViewer,)
    search_fields = ('name',)

    def perform_update(self, serializer):
        old_name = self.get_object().name
        instance = serializer.save()
        new_name = instance.name
        if old_name != new_name:
            # Synchronize companies with this city
            Company.objects.filter(city=old_name).update(city=new_name)


class BusinessTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Business Types directory (Кафе, Ресторан, etc.).
    """
    queryset = BusinessType.objects.all().order_by('name')
    serializer_class = BusinessTypeSerializer
    permission_classes = (ReadOnlyForViewer,)
    search_fields = ('name',)

    def perform_update(self, serializer):
        old_name = self.get_object().name
        instance = serializer.save()
        new_name = instance.name
        if old_name != new_name:
            Company.objects.filter(business_type=old_name).update(business_type=new_name)


class LicenceTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Licence Types directory (Cloud, LifeTime, etc.).
    """
    queryset = LicenceType.objects.all().order_by('name')
    serializer_class = LicenceTypeSerializer
    permission_classes = (ReadOnlyForViewer,)
    search_fields = ('name',)

    def perform_update(self, serializer):
        old_name = self.get_object().name
        instance = serializer.save()
        new_name = instance.name
        if old_name != new_name:
            Company.objects.filter(licence_type=old_name).update(licence_type=new_name)


class CompanyPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200


class CompanyViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Companies / Places of service.
    - Read operations available to VIEWER, MANAGER, SUPERADMIN.
    - Write operations restricted to MANAGER and SUPERADMIN.
    """
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = CompanyPagination
    search_fields = (
        'place_name', 'company_name', 'cabinet_name',
        'crm_id', 'uid', 'server_name', 'city'
    )
    filterset_fields = (
        'city', 'status', 'iiko_rosta', 'business_type',
        'licence_type', 'software_type', 'node_type', 'parent_chain',
        'helpdesk_its'
    )
    ordering_fields = (
        'place_name', 'city', 'status', 'updated_at', 'id', 'created_at',
        'software_type', 'node_type', 'sort_number', 'helpdesk_its', 'iiko_version', 'licence_type'
    )

    def get_queryset(self):
        # Annotate with effective_chain_id to group Chain + Branches together
        # If company has parent_chain, group by parent_chain_id. If it is Chain, group by its own id.
        from django.db.models import Q
        qs = Company.objects.select_related('parent_chain').prefetch_related('anydesk_stations', 'branches').annotate(
            effective_chain_id=Coalesce('parent_chain_id', 'id'),
            is_branch=Case(
                When(node_type='CHAIN', then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        )

        chain_id = self.request.query_params.get('chain_id')
        if chain_id:
            qs = qs.filter(Q(id=chain_id) | Q(parent_chain_id=chain_id))

        its = self.request.query_params.get('its')
        if its == 'yes':
            qs = qs.filter(helpdesk_its='Да', status=True)
        elif its == 'no':
            qs = qs.filter(Q(helpdesk_its='Нет') | Q(status=False) | Q(helpdesk_its__isnull=True) | Q(helpdesk_its=''))
        elif its in ['over_month', 'week_month', 'week', 'day', 'expired']:
            from datetime import date, timedelta
            today = date.today()
            qs = qs.filter(helpdesk_its='Да', status=True)
            if its == 'over_month':
                qs = qs.filter(its_expires_at__gt=today + timedelta(days=30))
            elif its == 'week_month':
                qs = qs.filter(
                    its_expires_at__gte=today + timedelta(days=8),
                    its_expires_at__lte=today + timedelta(days=30)
                )
            elif its == 'week':
                qs = qs.filter(
                    its_expires_at__gte=today + timedelta(days=1),
                    its_expires_at__lte=today + timedelta(days=7)
                )
            elif its == 'day':
                qs = qs.filter(its_expires_at=today)
            elif its == 'expired':
                qs = qs.filter(its_expires_at__lt=today)

        ordering = self.request.query_params.get('ordering', '')
        if not ordering or ordering == 'chain_smart':
            # Default smart sort:
            # 1. Newest chains and single establishments first (-effective_chain_id)
            # 2. Inside chain: Head Office (CHAIN) always first (is_branch=0), then branches (is_branch=1)
            # 3. Oldest to newest branch order (id)
            return qs.order_by('-effective_chain_id', 'is_branch', 'id')
        elif ordering == '-created_at':
            return qs.order_by('-created_at', '-id')
        elif ordering == 'place_name':
            return qs.order_by('place_name', 'id')
        elif ordering == '-place_name':
            return qs.order_by('-place_name', '-id')
        elif ordering == 'city':
            return qs.order_by('city', 'place_name')
        elif ordering in ('iiko_version', '-iiko_version'):
            from django.db import connection
            from django.db.models.expressions import RawSQL
            if connection.vendor == 'postgresql':
                # Semantic version array [9, 5, 8] for proper numerical comparison (e.g. 9.10 > 9.9)
                version_arr = RawSQL(
                    "CASE WHEN iiko_version ~ '^([0-9]+\\.)*[0-9]+$' THEN string_to_array(iiko_version, '.')::int[] ELSE NULL END",
                    ()
                )
                if ordering == 'iiko_version':
                    return qs.order_by(version_arr.asc(nulls_last=True), 'place_name', 'id')
                else:
                    return qs.order_by(version_arr.desc(nulls_last=True), 'place_name', 'id')
            else:
                if ordering == 'iiko_version':
                    return qs.order_by(F('iiko_version').asc(nulls_last=True), 'place_name', 'id')
                else:
                    return qs.order_by(F('iiko_version').desc(nulls_last=True), 'place_name', 'id')

        return qs.order_by(ordering)

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanyDetailSerializer

    @action(detail=False, methods=['get'])
    def chains(self, request):
        """
        Returns all CHAIN companies to populate Chain selector in create/edit modal.
        """
        chains = Company.objects.filter(
            node_type=Company.NodeType.CHAIN
        ).prefetch_related('branches').order_by('place_name')
        serializer = ChainOptionSerializer(chains, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """
        Returns distinct values for dropdown filters on the frontend.
        """
        cities = list(City.objects.values_list('name', flat=True).order_by('name'))
        if not cities:
            cities = list(Company.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city'))

        business_types = list(BusinessType.objects.values_list('name', flat=True).order_by('name'))
        if not business_types:
            business_types = list(Company.objects.exclude(business_type='').values_list('business_type', flat=True).distinct().order_by('business_type'))

        licence_types = list(LicenceType.objects.values_list('name', flat=True).order_by('name'))
        if not licence_types:
            licence_types = list(Company.objects.exclude(licence_type='').values_list('licence_type', flat=True).distinct().order_by('licence_type'))

        raw_versions = set()
        for v in IikoDistribution.objects.values_list('iiko_version', flat=True):
            cleaned = clean_iiko_version(v)
            if cleaned:
                raw_versions.add(cleaned)
        for v in Company.objects.exclude(iiko_version='').values_list('iiko_version', flat=True):
            cleaned = clean_iiko_version(v)
            if cleaned:
                raw_versions.add(cleaned)
        iiko_versions = sorted(list(raw_versions), key=version_sort_key, reverse=True)

        iiko_rosta_values = list(Company.objects.exclude(iiko_rosta='').values_list('iiko_rosta', flat=True).distinct().order_by('iiko_rosta'))

        chains = list(Company.objects.filter(node_type=Company.NodeType.CHAIN).values('id', 'place_name').order_by('place_name'))

        # Counts by software_type, status and its (both total establishments and unique companies/chains)
        def count_its_companies(qs):
            return qs.filter(helpdesk_its='Да', status=True).annotate(gid=Coalesce('parent_chain_id', 'id')).values('gid').distinct().count()

        total_count = Company.objects.count()
        active_count = Company.objects.filter(status=True).count()
        its_count = Company.objects.filter(helpdesk_its='Да', status=True).count()
        its_companies_count = count_its_companies(Company.objects.all())

        iiko_qs = Company.objects.filter(software_type=Company.SoftwareType.IIKO)
        iiko_count = iiko_qs.count()
        iiko_active_count = iiko_qs.filter(status=True).count()
        iiko_its_count = iiko_qs.filter(helpdesk_its='Да', status=True).count()
        iiko_its_companies_count = count_its_companies(iiko_qs)

        rosta_qs = Company.objects.filter(software_type=Company.SoftwareType.ROSTA)
        rosta_count = rosta_qs.count()
        rosta_active_count = rosta_qs.filter(status=True).count()
        rosta_its_count = rosta_qs.filter(helpdesk_its='Да', status=True).count()
        rosta_its_companies_count = count_its_companies(rosta_qs)

        return Response({
            'cities': cities,
            'business_types': business_types,
            'licence_types': licence_types,
            'iiko_versions': iiko_versions,
            'iiko_rosta': iiko_rosta_values,
            'chains': chains,
            'total_count': total_count,
            'active_count': active_count,
            'its_count': its_count,
            'its_companies_count': its_companies_count,
            'iiko_count': iiko_count,
            'iiko_active_count': iiko_active_count,
            'iiko_its_count': iiko_its_count,
            'iiko_its_companies_count': iiko_its_companies_count,
            'rosta_count': rosta_count,
            'rosta_active_count': rosta_active_count,
            'rosta_its_count': rosta_its_count,
            'rosta_its_companies_count': rosta_its_companies_count,
        })

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(updated_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(updated_by=user)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'SUPERADMIN':
            return Response(
                {"detail": "Удаление заведений разрешено только суперадминистратору."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def clearbat_params(self, request, pk=None):
        """
        Calculates and returns pre-encoded parameters for ClearBat protocol and helper launch.
        ClearBat SQLite database (Entities table) strictly requires passwords to be Base64-encoded.
        """
        company = self.get_object()
        server = company.server_name or ''
        port = company.port_number or '443'
        login = company.system_admin_name or 'iikoadm'
        password = company.get_password() or ''

        # Base64 encrypted/encoded password for ClearBat Entities SQLite
        clearbat_password = base64.b64encode(password.encode('utf-8')).decode('ascii') if password else ''

        # V2 parameter format from MS Access: ?type=iiko?url=host:port?login=user?password=pass
        raw_params = f"?type=iiko?url={server}:{port}?login={login}?password={password}"
        final_base64 = base64.b64encode(raw_params.encode('utf-8')).decode('ascii')
        full_url = f"clearbat:/{final_base64}?encode=full"

        # License updater URL: clearbat:/type=license?url=host:port?login=user?password=pass
        license_url = f"clearbat:/type=license?url={server}:{port}?login={login}?password={password}"

        return Response({
            'server': server,
            'port': port,
            'login': login,
            'password': password,
            'clearbat_password': clearbat_password,
            'raw_params': raw_params,
            'base64_params': final_base64,
            'clearbat_url': full_url,
            'license_url': license_url,
        })

    @action(detail=True, methods=['get', 'post'], url_path='license-data')
    def license_data(self, request, pk=None):
        company = self.get_object()

        if request.method == 'GET':
            return Response({
                'id': company.id,
                'place_name': company.place_name,
                'license_data': company.license_data or {},
                'license_updated_at': company.license_updated_at,
                'last_license_error': company.last_license_error or '',
            })

        # POST
        data = request.data
        task_id = data.get('task_id')
        log_text = data.get('log_text', '')

        # Direct error passed from agent
        if not data.get('success', True) or data.get('error'):
            err_msg = data.get('error', 'Неизвестная ошибка получения лицензии')
            company.last_license_error = err_msg
            company.save(update_fields=['last_license_error'])
            if task_id:
                try:
                    from apps.companion.services import set_task_status
                    set_task_status(task_id, {
                        'status': 'error',
                        'error': err_msg,
                        'company_id': company.id
                    })
                except Exception:
                    pass
            return Response({
                'success': False,
                'error': err_msg,
                'last_license_error': company.last_license_error
            }, status=status.HTTP_400_BAD_REQUEST)

        # Parse log_text if provided, or use provided license_data dict
        parsed = None
        if log_text:
            from .license_parser import parse_clearbat_license_log, is_license_active
            parsed = parse_clearbat_license_log(log_text)
        elif isinstance(data.get('license_data'), dict):
            from .license_parser import is_license_active
            parsed = data.get('license_data')
            if 'success' not in parsed:
                parsed['success'] = True
        else:
            from .license_parser import is_license_active

        if not parsed:
            return Response({
                'success': False,
                'error': 'Не переданы данные лицензии или текст лога'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not parsed.get('success'):
            err_msg = parsed.get('error', 'Ошибка разбора лога лицензий')
            company.last_license_error = err_msg
            company.save(update_fields=['last_license_error'])
            if task_id:
                try:
                    from apps.companion.services import set_task_status
                    set_task_status(task_id, {
                        'status': 'error',
                        'error': err_msg,
                        'company_id': company.id
                    })
                except Exception:
                    pass
            return Response({
                'success': False,
                'error': err_msg,
                'last_license_error': company.last_license_error
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if license is active/valid
        key_modules = data.get('key_modules')
        license_is_active = is_license_active(parsed, key_modules=key_modules)

        # Success - save license_data
        company.license_data = parsed
        company.license_updated_at = timezone.now()
        company.last_license_error = ''

        update_fields = ['license_data', 'license_updated_at', 'last_license_error']

        # Auto-activate company if active license is obtained successfully
        was_inactive = not company.status
        auto_activated = False
        if license_is_active and was_inactive:
            company.status = True
            update_fields.append('status')
            auto_activated = True

        # Auto-fill missing company attributes from parsed license
        if not company.crm_id and parsed.get('crm_id'):
            company.crm_id = str(parsed['crm_id']).strip()
            update_fields.append('crm_id')

        if not company.uid and parsed.get('uid'):
            company.uid = str(parsed['uid']).strip()
            update_fields.append('uid')

        # Synchronize and update iiko_version in company and IikoDistribution
        is_new_version = False
        if parsed.get('iiko_version'):
            raw_ver = str(parsed['iiko_version']).strip()
            synced_ver, is_new_version = sync_iiko_version_with_distributions(raw_ver, company.node_type)
            if company.iiko_version != synced_ver:
                company.iiko_version = synced_ver
                if 'iiko_version' not in update_fields:
                    update_fields.append('iiko_version')

        company.save(update_fields=update_fields)

        if task_id:
            try:
                from apps.companion.services import set_task_status
                set_task_status(task_id, {
                    'status': 'completed',
                    'company_id': company.id,
                    'modules_count': parsed.get('modules_count', 0),
                    'expiration': parsed.get('expiration'),
                    'is_active': company.status,
                    'auto_activated': auto_activated,
                    'is_new_version': is_new_version,
                    'iiko_version': company.iiko_version,
                })
            except Exception:
                pass

        return Response({
            'success': True,
            'message': 'Данные лицензии успешно сохранены' + (' (заведение автоматически активировано)' if auto_activated else ''),
            'is_active': company.status,
            'auto_activated': auto_activated,
            'is_new_version': is_new_version,
            'iiko_version': company.iiko_version,
            'license_data': company.license_data,
            'license_updated_at': company.license_updated_at,
            'company': {
                'id': company.id,
                'status': company.status,
                'crm_id': company.crm_id,
                'uid': company.uid,
                'iiko_version': company.iiko_version,
            }
        }, status=status.HTTP_200_OK)


class AnydeskStationViewSet(viewsets.ModelViewSet):
    """
    CRUD API for AnyDesk Stations.
    """
    queryset = AnydeskStation.objects.select_related('company').all()
    serializer_class = AnydeskStationSerializer
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = CompanyPagination
    search_fields = (
        'anydesk_id', 'description',
        'company__place_name', 'company__company_name', 'company__city'
    )
    filterset_fields = ('company',)
    ordering_fields = ('id', 'description', 'anydesk_id', 'company__place_name')
    ordering = ('-id',)


class IikoDistributionViewSet(viewsets.ModelViewSet):
    """
    Registry of iiko Office distributions and Yandex Disk links.
    """
    queryset = IikoDistribution.objects.all()
    serializer_class = IikoDistributionSerializer
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = None
    search_fields = ('iiko_version', 'type')
    filterset_fields = ('type', 'iiko_version')
    ordering = ('-iiko_version',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        items = list(queryset)
        items.sort(key=lambda x: version_sort_key(x.iiko_version), reverse=True)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def versions(self, request):
        """
        Returns list of distinct available iiko versions for dropdowns.
        """
        versions = list(
            IikoDistribution.objects.values_list('iiko_version', flat=True).distinct()
        )
        versions = sorted(versions, key=version_sort_key, reverse=True)
        return Response(versions)


class AnydeskVersionViewSet(viewsets.ModelViewSet):
    """
    CRUD API for AnyDesk profiles and Sandboxie configurations.
    """
    queryset = AnydeskVersion.objects.all().order_by('order', 'id')
    serializer_class = AnydeskVersionSerializer
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = None
    search_fields = ('name', 'sandbox_params', 'exe_path')
    ordering_fields = ('order', 'id', 'name', 'is_sandbox')


class ServiceTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Service Catalog types (ИТС, Сервер noIP, WhatsApp рассылка, etc.)
    """
    queryset = ServiceType.objects.all().order_by('-is_its', 'name')
    serializer_class = ServiceTypeSerializer
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = None
    search_fields = ('name', 'code', 'description')


class CompanyServiceViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Company Services / Subscriptions.
    """
    queryset = CompanyService.objects.select_related('company', 'company__parent_chain', 'service').all()
    serializer_class = CompanyServiceSerializer
    permission_classes = (ReadOnlyForViewer,)
    pagination_class = None
    search_fields = (
        'company__place_name', 'company__company_name', 'company__city',
        'service_name', 'service__name', 'comment'
    )
    filterset_fields = ('company', 'service', 'status', 'period_type', 'pricing_type')
    ordering_fields = ('expires_at', 'company__place_name', 'total_cost', 'created_at')
    ordering = ('expires_at',)

    def get_queryset(self):
        # Services are rendered ONLY to active establishments
        qs = super().get_queryset().filter(company__status=True)

        exp_status = self.request.query_params.get('exp_status')
        from datetime import date, timedelta
        today = date.today()
        if exp_status == 'over_month':
            qs = qs.filter(expires_at__gt=today + timedelta(days=30), status=True)
        elif exp_status == 'week_month':
            qs = qs.filter(expires_at__gte=today + timedelta(days=8), expires_at__lte=today + timedelta(days=30), status=True)
        elif exp_status == 'week':
            qs = qs.filter(expires_at__gte=today + timedelta(days=1), expires_at__lte=today + timedelta(days=7), status=True)
        elif exp_status == 'day':
            qs = qs.filter(expires_at=today, status=True)
        elif exp_status == 'expired':
            qs = qs.filter(expires_at__lt=today)
        elif exp_status == 'active':
            qs = qs.filter(expires_at__gte=today, status=True)

        is_its = self.request.query_params.get('is_its')
        if is_its == 'true':
            qs = qs.filter(service__is_its=True)
        elif is_its == 'false':
            qs = qs.filter(service__is_its=False)

        node_type = self.request.query_params.get('node_type')
        if node_type:
            qs = qs.filter(company__node_type=node_type)

        return qs

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        Quick renewal of a subscription:
        Payload options:
          - months: integer (1, 3, 6, 12)
          - new_date: 'YYYY-MM-DD'
        """
        sub = self.get_object()
        from datetime import date
        import calendar

        months = request.data.get('months')
        new_date_str = request.data.get('new_date')

        if new_date_str:
            from datetime import datetime
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        elif months:
            months = int(months)
            base_date = sub.expires_at if sub.expires_at and sub.expires_at >= date.today() else date.today()
            month = base_date.month - 1 + months
            year = base_date.year + month // 12
            month = month % 12 + 1
            day = min(base_date.day, calendar.monthrange(year, month)[1])
            new_date = date(year, month, day)
        else:
            return Response({'error': 'Укажите months или new_date'}, status=status.HTTP_400_BAD_REQUEST)

        sub.expires_at = new_date
        sub.status = True
        sub.save()

        serializer = self.get_serializer(sub)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Returns KPI statistics for ITS and services dashboard.
        """
        from datetime import date, timedelta
        from django.db.models import Sum
        today = date.today()

        all_subs = CompanyService.objects.filter(status=True, company__status=True)
        its_subs = all_subs.filter(service__is_its=True)

        over_month = its_subs.filter(expires_at__gt=today + timedelta(days=30)).count()
        week_month = its_subs.filter(expires_at__gte=today + timedelta(days=8), expires_at__lte=today + timedelta(days=30)).count()
        week = its_subs.filter(expires_at__gte=today + timedelta(days=1), expires_at__lte=today + timedelta(days=7)).count()
        day = its_subs.filter(expires_at=today).count()
        expired = CompanyService.objects.filter(service__is_its=True, company__status=True, expires_at__lt=today).count()

        total_points = 0
        its_companies_count = its_subs.values('company').distinct().count()
        for s in its_subs.select_related('company'):
            if s.pricing_type in [CompanyService.PricingType.PER_RMS, CompanyService.PricingType.PER_FRONT]:
                total_points += s.quantity if (s.quantity and s.quantity > 0) else 1
            elif s.company.node_type == Company.NodeType.CHAIN:
                total_points += max(s.company.branches.filter(status=True).count(), 1)
            else:
                total_points += 1

        total_monthly_sum = None
        user = request.user
        if user and user.is_authenticated and getattr(user, 'role', '') in ['SUPERADMIN', 'MANAGER']:
            total_monthly_sum = float(all_subs.aggregate(s=Sum('total_cost'))['s'] or 0)

        return Response({
            'total_its_companies': its_companies_count,
            'total_its_points': total_points,
            'over_month': over_month,
            'week_month': week_month,
            'week': week,
            'day': day,
            'expired': expired,
            'total_monthly_sum': total_monthly_sum,
        })
