from django.contrib import admin
from .models import Company, AnydeskStation, IikoDistribution

class AnydeskStationInline(admin.TabularInline):
    model = AnydeskStation
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'place_name', 'company_name', 'crm_id', 'uid', 'city', 'business_type', 'licence_type', 'status')
    list_filter = ('city', 'status', 'iiko_rosta', 'business_type', 'licence_type')
    search_fields = ('place_name', 'company_name', 'cabinet_name', 'crm_id', 'uid', 'server_name', 'city')
    inlines = [AnydeskStationInline]

@admin.register(AnydeskStation)
class AnydeskStationAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'description', 'anydesk_id', 'any_pass')
    search_fields = ('anydesk_id', 'description', 'company__place_name')
    list_filter = ('company__city',)

@admin.register(IikoDistribution)
class IikoDistributionAdmin(admin.ModelAdmin):
    list_display = ('id', 'iiko_version', 'type', 'link_ya')
    search_fields = ('iiko_version', 'type')
