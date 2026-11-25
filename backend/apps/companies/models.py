from django.db import models
from django.conf import settings
from apps.common.crypto import encrypt_password, decrypt_password
from .utils import clean_iiko_version, invalidate_distribution_cache

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название города')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Тип заведения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Тип заведения'
        verbose_name_plural = 'Типы заведений'
        ordering = ['name']

    def __str__(self):
        return self.name


class LicenceType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Тип лицензии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Тип лицензии'
        verbose_name_plural = 'Типы лицензий'
        ordering = ['name']

    def __str__(self):
        return self.name


class Company(models.Model):
    class SoftwareType(models.TextChoices):
        IIKO = 'IIKO', 'iiko'
        ROSTA = 'ROSTA', 'Rosta'

    class NodeType(models.TextChoices):
        CHAIN = 'CHAIN', 'Chain (Сеть / ГО)'
        RMS = 'RMS', 'RMS (Точка / Филиал)'

    # Основная идентификация системы и типа узла
    software_type = models.CharField(
        max_length=20,
        choices=SoftwareType.choices,
        default=SoftwareType.IIKO,
        db_index=True,
        verbose_name='Система автоматизации'
    )
    node_type = models.CharField(
        max_length=20,
        choices=NodeType.choices,
        default=NodeType.RMS,
        db_index=True,
        verbose_name='Тип узла (Chain/RMS)'
    )
    parent_chain = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branches',
        verbose_name='Головная организация сети (Chain)'
    )

    place_name = models.CharField(max_length=255, verbose_name='Название заведения')
    company_name = models.CharField(max_length=255, blank=True, verbose_name='Юр. лицо / Компания')
    bin = models.CharField(max_length=20, blank=True, db_index=True, verbose_name='БИН / ИИН')
    cabinet_name = models.CharField(max_length=255, blank=True, verbose_name='Название кабинета')
    crm_id = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='CRM ID')
    uid = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='UID')
    system_admin_name = models.CharField(max_length=100, blank=True, default='iikoadm', verbose_name='Логин сисадмина')
    system_admin_password_enc = models.TextField(blank=True, verbose_name='Зашифрованный пароль сисадмина')
    business_type = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='Тип заведения')
    licence_type = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='Тип лицензии')
    iiko_version = models.CharField(max_length=100, blank=True, verbose_name='Версия iiko')
    server_name = models.CharField(max_length=255, blank=True, db_index=True, verbose_name='Сервер / Домен')
    port_number = models.CharField(max_length=20, blank=True, default='443', verbose_name='Порт')
    image_link = models.TextField(blank=True, verbose_name='Ссылка на изображение')
    no_ip = models.CharField(max_length=50, blank=True, verbose_name='No-IP / DDNS')
    iiko_rosta = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='iiko Rosta')
    sort_number = models.IntegerField(null=True, blank=True, db_index=True, verbose_name='Порядок сортировки / ID сети')
    helpdesk_its = models.CharField(max_length=50, blank=True, verbose_name='HelpDesk ITS')
    its_expires_at = models.DateField(null=True, blank=True, db_index=True, verbose_name='Срок действия ИТС')
    its_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Стоимость ИТС (₸)')
    city = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='Город')
    status = models.BooleanField(default=True, db_index=True, verbose_name='Активен')
    iiko_web_address = models.TextField(blank=True, verbose_name='Адрес iikoWeb')
    license_data = models.JSONField(default=dict, blank=True, verbose_name='Информация о лицензиях')
    license_updated_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата обновления лицензии')
    last_license_error = models.TextField(blank=True, verbose_name='Последняя ошибка обновления лицензии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_companies',
        verbose_name='Автор обновления'
    )

    class Meta:
        verbose_name = 'Заведение (Клиент)'
        verbose_name_plural = 'Заведения (Клиенты)'
        ordering = ['place_name', 'id']

    def __str__(self):
        type_str = f"[{self.node_type}] " if self.node_type == self.NodeType.CHAIN else ""
        return f"{type_str}{self.place_name} ({self.city or 'Без города'})"

    def set_password(self, plain_password: str):
        self.system_admin_password_enc = encrypt_password(plain_password)

    def get_password(self) -> str:
        return decrypt_password(self.system_admin_password_enc)

    def save(self, *args, **kwargs):
        if not self.status:
            self.helpdesk_its = 'Нет'
            self.its_expires_at = None
            self.its_cost = 0
            if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                kwargs['update_fields'] = list(set(kwargs['update_fields']) | {'helpdesk_its', 'its_expires_at', 'its_cost'})
        else:
            if self.its_cost is None:
                self.its_cost = 0
                if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                    kwargs['update_fields'] = list(set(kwargs['update_fields']) | {'its_cost'})
            if self.pk:
                try:
                    # If activating an establishment that has active ITS subscriptions, restore ITS parameters
                    active_its = self.company_services.filter(status=True, service__is_its=True).order_by('-expires_at').first()
                    if active_its:
                        self.helpdesk_its = 'Да'
                        if not self.its_expires_at:
                            self.its_expires_at = active_its.expires_at
                        self.its_cost = active_its.total_cost
                        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                            kwargs['update_fields'] = list(set(kwargs['update_fields']) | {'helpdesk_its', 'its_expires_at', 'its_cost'})
                    elif self.node_type == self.NodeType.RMS and self.parent_chain and self.parent_chain.helpdesk_its == 'Да':
                        self.helpdesk_its = 'Да'
                        if not self.its_expires_at:
                            self.its_expires_at = self.parent_chain.its_expires_at
                        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                            kwargs['update_fields'] = list(set(kwargs['update_fields']) | {'helpdesk_its', 'its_expires_at'})
                except Exception:
                    pass

        if self.iiko_version:
            self.iiko_version = clean_iiko_version(self.iiko_version)
        super().save(*args, **kwargs)


class AnydeskStation(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='anydesk_stations',
        verbose_name='Заведение'
    )
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание рабочего места')
    anydesk_id = models.CharField(max_length=50, db_index=True, verbose_name='AnyDesk ID')
    any_pass = models.CharField(max_length=100, blank=True, verbose_name='Пароль AnyDesk')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Станция AnyDesk'
        verbose_name_plural = 'Станции AnyDesk'
        ordering = ['company', 'description', 'id']

    def __str__(self):
        return f"{self.company.place_name} — {self.description or self.anydesk_id}"


class IikoDistribution(models.Model):
    iiko_version = models.CharField(max_length=100, db_index=True, verbose_name='Версия iiko')
    type = models.CharField(max_length=50, default='RMS', verbose_name='Тип (RMS / Chain)')
    link_ya = models.TextField(verbose_name='Ссылка на Яндекс.Диск')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Дистрибутив iiko'
        verbose_name_plural = 'Дистрибутивы iiko'
        ordering = ['-iiko_version']

    def __str__(self):
        return f"iiko {self.iiko_version} ({self.type})"

    def save(self, *args, **kwargs):
        if self.iiko_version:
            self.iiko_version = clean_iiko_version(self.iiko_version)
        invalidate_distribution_cache()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        invalidate_distribution_cache()
        super().delete(*args, **kwargs)


class AnydeskVersion(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название профиля')
    exe_path = models.CharField(
        max_length=500,
        blank=True,
        default=r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe',
        verbose_name='Путь к AnyDesk.exe'
    )
    is_sandbox = models.BooleanField(default=False, verbose_name='Запуск через песочницу (Sandboxie)')
    sandbox_params = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Параметры песочницы (/box:...)'
    )
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Версия / Профиль AnyDesk'
        verbose_name_plural = 'Версии / Профили AnyDesk'
        ordering = ['order', 'id']

    def __str__(self):
        sandbox_tag = f" [Sandbox: {self.sandbox_params}]" if self.is_sandbox else ""
        return f"{self.name}{sandbox_tag}"


class ServiceType(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название услуги')
    code = models.CharField(max_length=50, blank=True, verbose_name='Код услуги')
    is_its = models.BooleanField(default=False, db_index=True, verbose_name='Является базовым ИТС')
    description = models.TextField(blank=True, verbose_name='Описание услуги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Вид услуги'
        verbose_name_plural = 'Каталог услуг'
        ordering = ['-is_its', 'name']

    def __str__(self):
        return self.name


class CompanyService(models.Model):
    class PricingType(models.TextChoices):
        MANUAL = 'MANUAL', 'Фиксированная сумма'
        PER_RMS = 'PER_RMS', 'За каждую точку (RMS)'
        PER_FRONT = 'PER_FRONT', 'За каждый Front'

    class PeriodType(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Ежемесячная подписка'
        QUARTERLY = 'QUARTERLY', 'Квартальная'
        YEARLY = 'YEARLY', 'Годовая'
        ONE_TIME = 'ONE_TIME', 'Разовая'

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_services',
        verbose_name='Компания / Заведение'
    )
    service = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Услуга'
    )
    service_name = models.CharField(max_length=150, blank=True, verbose_name='Название услуги')
    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
        default=PeriodType.MONTHLY,
        verbose_name='Период / Тариф'
    )
    pricing_type = models.CharField(
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.MANUAL,
        verbose_name='Метод расчёта стоимости'
    )
    cost_per_rms = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Ставка за 1 ед. (RMS / Front) (₸)'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество точек / касс'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Итоговая стоимость (₸)'
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    expires_at = models.DateField(db_index=True, verbose_name='Срок действия до')
    status = models.BooleanField(default=True, db_index=True, verbose_name='Активна')
    comment = models.TextField(blank=True, verbose_name='Комментарий / Договор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Услуга компании'
        verbose_name_plural = 'Услуги компаний'
        ordering = ['expires_at', 'company__place_name']

    def __str__(self):
        return f"{self.company.place_name} — {self.service_name or self.service.name} (до {self.expires_at})"

    def calculate_cost(self):
        if self.pricing_type in [self.PricingType.PER_RMS, self.PricingType.PER_FRONT]:
            qty = self.quantity if (self.quantity is not None and self.quantity > 0) else 1
            return self.cost_per_rms * qty
        return self.total_cost

    def save(self, *args, **kwargs):
        old_company_id = None
        if self.pk:
            try:
                old_inst = CompanyService.objects.only('company_id').get(pk=self.pk)
                if old_inst.company_id != self.company_id:
                    old_company_id = old_inst.company_id
            except CompanyService.DoesNotExist:
                pass

        if not self.service_name and self.service_id:
            self.service_name = self.service.name
        if self.pricing_type in [self.PricingType.PER_RMS, self.PricingType.PER_FRONT] and self.cost_per_rms > 0:
            qty = self.quantity if (self.quantity is not None and self.quantity > 0) else 1
            self.total_cost = self.cost_per_rms * qty
        super().save(*args, **kwargs)

        # Synchronize Company.helpdesk_its and its_expires_at if this is an ITS service
        if self.service and self.service.is_its:
            if self.status and self.company.status:
                Company.objects.filter(id=self.company_id, status=True).update(
                    helpdesk_its='Да',
                    its_expires_at=self.expires_at,
                    its_cost=self.total_cost
                )
                if self.company.node_type == Company.NodeType.CHAIN:
                    # ONLY active branches receive ITS! Inactive branches must not get ITS.
                    self.company.branches.filter(status=True).update(
                        helpdesk_its='Да',
                        its_expires_at=self.expires_at
                    )
                    self.company.branches.filter(status=False).update(
                        helpdesk_its='Нет',
                        its_expires_at=None,
                        its_cost=0
                    )
            else:
                has_active = CompanyService.objects.filter(company_id=self.company_id, service__is_its=True, status=True).exclude(pk=self.pk).exists()
                if not has_active:
                    Company.objects.filter(id=self.company_id).update(
                        helpdesk_its='Нет',
                        its_expires_at=None,
                        its_cost=0
                    )
                    if self.company.node_type == Company.NodeType.CHAIN:
                        self.company.branches.update(
                            helpdesk_its='Нет',
                            its_expires_at=None,
                            its_cost=0
                        )

            if old_company_id:
                has_active_old = CompanyService.objects.filter(company_id=old_company_id, service__is_its=True, status=True).exists()
                if not has_active_old:
                    Company.objects.filter(id=old_company_id).update(
                        helpdesk_its='Нет',
                        its_expires_at=None,
                        its_cost=0
                    )
                    old_comp = Company.objects.filter(id=old_company_id).first()
                    if old_comp and old_comp.node_type == Company.NodeType.CHAIN:
                        old_comp.branches.update(
                            helpdesk_its='Нет',
                            its_expires_at=None,
                            its_cost=0
                        )

    def delete(self, *args, **kwargs):
        cid = self.company_id
        is_its = bool(self.service and self.service.is_its)
        super().delete(*args, **kwargs)
        if is_its:
            has_other = CompanyService.objects.filter(company_id=cid, service__is_its=True, status=True).exists()
            if not has_other:
                Company.objects.filter(id=cid).update(
                    helpdesk_its='Нет',
                    its_expires_at=None,
                    its_cost=0
                )
                comp = Company.objects.filter(id=cid).first()
                if comp and comp.node_type == Company.NodeType.CHAIN:
                    comp.branches.update(
                        helpdesk_its='Нет',
                        its_expires_at=None,
                        its_cost=0
                    )

