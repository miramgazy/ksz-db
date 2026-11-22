from django.urls import path
from .views import (
    CompanionStatusView,
    CompanionLaunchBackofficeView,
    CompanionLaunchLicenseView,
    CompanionInsertClearbatView,
    CompanionLaunchAnydeskView,
    CompanionAgentPollView,
    CompanionAgentResultView,
)

urlpatterns = [
    # Frontend browser endpoints
    path('status/', CompanionStatusView.as_view(), name='companion_status'),
    path('launch-backoffice/', CompanionLaunchBackofficeView.as_view(), name='companion_launch_backoffice'),
    path('launch-license/', CompanionLaunchLicenseView.as_view(), name='companion_launch_license'),
    path('insert-clearbat/', CompanionInsertClearbatView.as_view(), name='companion_insert_clearbat'),
    path('launch-anydesk/', CompanionLaunchAnydeskView.as_view(), name='companion_launch_anydesk'),

    # Local agent (ksz_helper.py) endpoints
    path('agent/poll/', CompanionAgentPollView.as_view(), name='companion_agent_poll'),
    path('agent/result/', CompanionAgentResultView.as_view(), name='companion_agent_result'),
]
