from django.db import models
from apps.companies.models import Company


class WebkassaCTO(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название ЦТО')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Обслуживающее ЦТО'
        verbose_name_plural = 'Обслуживающие ЦТО'
        ordering = ['name']

    def __str__(self):
        return self.name


class WebkassaCashRegister(models.Model):
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Активна')
    cto = models.CharField(max_length=150, blank=True, db_index=True, verbose_name='Обслуживающее ЦТО')
    name = models.CharField(max_length=255, verbose_name='Название кассы')
    serial_number = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Заводской номер')
    status = models.CharField(max_length=100, blank=True, verbose_name='Статус')
    ofd = models.CharField(max_length=255, blank=True, verbose_name='ОФД')
    bin_iin = models.CharField(max_length=30, blank=True, db_index=True, verbose_name='БИН / ИИН')
    organization = models.CharField(max_length=255, blank=True, db_index=True, verbose_name='Организация (из WebKassa)')
    expires_at = models.DateField(null=True, blank=True, db_index=True, verbose_name='Срок окончания')
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_registers',
        verbose_name='Привязанное заведение'
    )
    auto_matched = models.BooleanField(default=False, verbose_name='Привязано автоматически по БИН/ИИН')
    comment = models.TextField(blank=True, verbose_name='Примечание инженера')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Касса WebKassa'
        verbose_name_plural = 'Кассы WebKassa'
        ordering = ['expires_at', 'name']

    def __str__(self):
        return f"{self.serial_number} — {self.name} ({self.organization or 'Без орг.'})"
