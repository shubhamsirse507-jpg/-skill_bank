from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('create/<int:exchange_id>/', views.create_booking, name='create_booking'),
    path('batches/', views.batches_view, name='batches'),
    path('batches/join/<int:batch_id>/', views.join_batch, name='join_batch'),
    path('live/', views.live_sessions_view, name='live_sessions'),
    path('doubt/', views.doubt_view, name='doubt'),          # ← redirects to live_sessions
    path('doubt/create/', views.create_doubt, name='create_doubt'),
    path('room/<str:room_id>/', views.live_room, name='live_room'),
]

