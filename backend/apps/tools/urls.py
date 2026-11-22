from django.urls import path
from .views import PasswordGeneratorView, DashboardStatsView

urlpatterns = [
    path('generate-password/', PasswordGeneratorView.as_view(), name='generate_password'),
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]
