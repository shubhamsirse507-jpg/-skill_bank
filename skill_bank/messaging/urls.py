from django.urls import path
from . import views

urlpatterns = [
    path('', views.messaging_view, name='messaging_index'),
    path('messages/', views.messaging_view, name='messaging'),
    path('messages/<int:exchange_id>/', views.messaging_view, name='messaging_detail'),
    path('messages/<int:exchange_id>/send/', views.send_message_ajax, name='send_message_ajax'),
]
