from django.urls import path
from . import views

urlpatterns = [
    path('learning/', views.learning_list, name='learning-list'),
    path('learning/<int:pk>/', views.learning_detail, name='learning-detail'),
]