from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IikoDistributionViewSet

router = DefaultRouter()
router.register('', IikoDistributionViewSet, basename='iiko-distributions')

urlpatterns = [
    path('', include(router.urls)),
]
