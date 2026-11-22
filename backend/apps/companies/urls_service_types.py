from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceTypeViewSet

router = DefaultRouter()
router.register('', ServiceTypeViewSet, basename='service-types')

urlpatterns = [
    path('', include(router.urls)),
]
