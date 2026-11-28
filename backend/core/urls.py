from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('administrator/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('apps.accounts.urls_auth')),
    path('api/v1/users/', include('apps.accounts.urls_users')),
    path('api/v1/companies/', include('apps.companies.urls_companies')),
    path('api/v1/cities/', include('apps.companies.urls_cities')),
    path('api/v1/business-types/', include('apps.companies.urls_business_types')),
    path('api/v1/departments/', include('apps.companies.urls_departments')),
    path('api/v1/licence-types/', include('apps.companies.urls_licence_types')),
    path('api/v1/anydesk/', include('apps.companies.urls_anydesk')),
    path('api/v1/anydesk-versions/', include('apps.companies.urls_anydesk_versions')),
    path('api/v1/iiko-distributions/', include('apps.companies.urls_distributions')),
    path('api/v1/service-types/', include('apps.companies.urls_service_types')),
    path('api/v1/company-services/', include('apps.companies.urls_company_services')),
    path('api/v1/tools/', include('apps.tools.urls')),
    path('api/v1/companion/', include('apps.companion.urls')),
    path('api/v1/webkassa/', include('apps.webkassa.urls')),

    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
