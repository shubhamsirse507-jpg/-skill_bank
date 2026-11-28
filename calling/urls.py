from django.urls import path

from .views import (
    CallingPermissionsAPIView,
    CallingSessionTokenAPIView,
    CallingSettingsAPIView,
    MyCallLogsAPIView,
)

app_name = 'calling'

urlpatterns = [
    path('token/', CallingSessionTokenAPIView.as_view(), name='calling_token'),
    path('permissions/', CallingPermissionsAPIView.as_view(), name='calling_permissions'),
    path('settings/', CallingSettingsAPIView.as_view(), name='calling_settings'),
    path('logs/', MyCallLogsAPIView.as_view(), name='calling_logs'),
]
