from django.urls import path
from . import views

urlpatterns = [
    path('', views.rating_view, name='rating_dashboard'),
    path('ratings/', views.rating_view, name='ratings_list'),
]
