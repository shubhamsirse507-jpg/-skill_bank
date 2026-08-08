from django.urls import path
from profiles import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('<str:username>/', views.public_profile, name='public_profile'),
]
