from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyServiceViewSet

router = DefaultRouter()
router.register('', CompanyServiceViewSet, basename='company-services')

urlpatterns = [
    path('', include(router.urls)),
]
