from datetime import date, timedelta
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.common.permissions import ReadOnlyForViewer
from apps.common.search import apply_smart_search
from apps.common.pagination import StandardResultsSetPagination
from .models import WebkassaCTO, WebkassaCashRegister
from .serializers import WebkassaCTOSerializer, WebkassaCashRegisterSerializer
from .services import import_webkassa_csv


class WebkassaCashRegisterViewSet(viewsets.ModelViewSet):
    queryset = WebkassaCashRegister.objects.select_related('company').all()
    serializer_class = WebkassaCashRegisterSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (ReadOnlyForViewer,)
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    search_fields = (
        'name', 'serial_number', 'bin_iin', 'organization',
        'cto', 'status', 'ofd', 'company__place_name',
        'company__company_name', 'company__city'
    )
    ordering_fields = (
        'is_active', 'expires_at', 'name', 'serial_number', 'cto', 'status',
        'organization', 'bin_iin', 'created_at', 'updated_at'
    )
    ordering = ('-is_active', 'expires_at', 'name')

    def get_queryset(self):
        qs = super().get_queryset()

        # 0. Фильтр по активности (Активна / Не активна)
        is_active = self.request.query_params.get('is_active')
        if is_active in ('true', '1'):
            qs = qs.filter(is_active=True)
        elif is_active in ('false', '0'):
            qs = qs.filter(is_active=False)

        # 1. Фильтр по обслуживающему ЦТО
        cto = self.request.query_params.get('cto')
        if cto and cto.strip() and cto != 'all':
            qs = qs.filter(cto=cto.strip())

        # 2. Фильтр по статусу кассы (Готова к работе, Заблокирована)
        st = self.request.query_params.get('status')
        if st and st.strip() and st != 'all':
            qs = qs.filter(status__iexact=st.strip())

        # 3. Фильтр по привязке к заведению: 'matched' (привязана) или 'unmatched' (без заведения)
        matched = self.request.query_params.get('matched')
        if matched == 'matched' or matched == 'true':
            qs = qs.filter(company__isnull=False)
        elif matched == 'unmatched' or matched == 'false':
            qs = qs.filter(company__isnull=True)

        # 4. Фильтр по конкретному заведению (company_id)
        company_id = self.request.query_params.get('company_id')
        if company_id:
            qs = qs.filter(company_id=company_id)

        # 5. Градация по срокам окончания (Дэшборд)
        gradation = self.request.query_params.get('gradation')
        today = date.today()
        if gradation:
            if gradation == 'expired':
                qs = qs.filter(expires_at__lt=today)
            elif gradation == 'day1':
                qs = qs.filter(expires_at__gte=today, expires_at__lte=today + timedelta(days=1))
            elif gradation == 'days3':
                qs = qs.filter(expires_at__gte=today, expires_at__lte=today + timedelta(days=3))
            elif gradation == 'days7':
                qs = qs.filter(expires_at__gte=today, expires_at__lte=today + timedelta(days=7))
            elif gradation == 'days15':
                qs = qs.filter(expires_at__gte=today, expires_at__lte=today + timedelta(days=15))
            elif gradation == 'days30':
                qs = qs.filter(expires_at__gte=today, expires_at__lte=today + timedelta(days=30))
            elif gradation == 'active_over30':
                qs = qs.filter(expires_at__gt=today + timedelta(days=30))

        # 6. Умный поиск (с нормализацией казахских букв и переключением раскладки)
        search_query = self.request.query_params.get('search', '').strip()
        if search_query:
            qs = apply_smart_search(qs, search_query, self.search_fields)

        return qs

    @action(detail=False, methods=['post'], url_path='upload-csv')
    def upload_csv(self, request):
        """Загрузка CSV файла WebKassa с предварительно указанным ЦТО."""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'Файл не прикреплен. Выберите файл в формате .csv'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cto = request.data.get('cto', '').strip()
        if not cto:
            return Response(
                {'error': 'Пожалуйста, укажите или выберите обслуживающее ЦТО.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_bytes = file_obj.read()
            stats = import_webkassa_csv(file_bytes, cto)
            return Response({
                'success': True,
                'message': f"Импорт завершен. Всего касс: {stats['total']}, добавлено: {stats['created']}, обновлено: {stats['updated']}.",
                'stats': stats
            })
        except Exception as e:
            return Response(
                {'error': f'Ошибка при обработке CSV файла: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Возвращает агрегированные метрики дэшборда по срокам окончания касс."""
        today = date.today()
        base_qs = WebkassaCashRegister.objects.all()

        cto = request.query_params.get('cto')
        if cto and cto != 'all':
            base_qs = base_qs.filter(cto=cto.strip())

        is_active = request.query_params.get('is_active')
        if is_active in ('true', '1'):
            base_qs = base_qs.filter(is_active=True)
        elif is_active in ('false', '0'):
            base_qs = base_qs.filter(is_active=False)

        def get_stats_for_qs(q_filter):
            filtered = base_qs.filter(q_filter)
            count = filtered.count()
            companies_count = (
                filtered.exclude(company__isnull=True)
                .values('company_id')
                .distinct()
                .count()
            )
            return {'count': count, 'companies_count': companies_count}

        expired = get_stats_for_qs(Q(expires_at__lt=today))
        day1 = get_stats_for_qs(Q(expires_at__gte=today, expires_at__lte=today + timedelta(days=1)))
        days3 = get_stats_for_qs(Q(expires_at__gte=today, expires_at__lte=today + timedelta(days=3)))
        days7 = get_stats_for_qs(Q(expires_at__gte=today, expires_at__lte=today + timedelta(days=7)))
        days15 = get_stats_for_qs(Q(expires_at__gte=today, expires_at__lte=today + timedelta(days=15)))
        days30 = get_stats_for_qs(Q(expires_at__gte=today, expires_at__lte=today + timedelta(days=30)))
        active_over30 = get_stats_for_qs(Q(expires_at__gt=today + timedelta(days=30)))

        total = base_qs.count()
        unmatched = base_qs.filter(company__isnull=True).count()
        matched = total - unmatched

        return Response({
            'expired': expired,
            'day1': day1,
            'days3': days3,
            'days7': days7,
            'days15': days15,
            'days30': days30,
            'active_over30': active_over30,
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
        })

    @action(detail=False, methods=['get'], url_path='cto-list')
    def cto_list(self, request):
        """Возвращает список всех известных названий ЦТО для автодополнения и фильтрации."""
        from_model = set(WebkassaCTO.objects.values_list('name', flat=True))
        from_registers = set(WebkassaCashRegister.objects.exclude(cto='').values_list('cto', flat=True))
        all_cto = sorted(list(from_model | from_registers))
        return Response(all_cto)


class WebkassaCTOViewSet(viewsets.ModelViewSet):
    queryset = WebkassaCTO.objects.all()
    serializer_class = WebkassaCTOSerializer
    permission_classes = (ReadOnlyForViewer,)
