from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnydeskVersionViewSet

router = DefaultRouter()
router.register('', AnydeskVersionViewSet, basename='anydesk-versions')

urlpatterns = [
    path('', include(router.urls)),
]
