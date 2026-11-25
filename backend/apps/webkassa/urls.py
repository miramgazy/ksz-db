from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebkassaCashRegisterViewSet, WebkassaCTOViewSet

router = DefaultRouter()
router.register(r'registers', WebkassaCashRegisterViewSet, basename='webkassa_registers')
router.register(r'cto', WebkassaCTOViewSet, basename='webkassa_cto')

urlpatterns = [
    path('', include(router.urls)),
]
