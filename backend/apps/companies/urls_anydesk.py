from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnydeskStationViewSet

router = DefaultRouter()
router.register('', AnydeskStationViewSet, basename='anydesk')

urlpatterns = [
    path('', include(router.urls)),
]
