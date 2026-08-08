from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('', views.rating_view, name='rating_dashboard'),
    path('api/', views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('api/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
]
