from django.urls import path
from chatboat import views

urlpatterns = [
    path('', views.chat, name='chatboat'),
    path('api/send/', views.chat_api, name='chatboat_api'),
]
