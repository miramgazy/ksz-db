from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessTypeViewSet

router = DefaultRouter()
router.register('', BusinessTypeViewSet, basename='business-types')

urlpatterns = [
    path('', include(router.urls)),
]
