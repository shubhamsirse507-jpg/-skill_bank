from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test_ui/', views.test_ui, name='test_ui'),

    path('add_doubt/', views.add_doubt, name='add_doubt'),
    path('view_doubt/', views.view_doubt, name='view_doubt'),

    path('book_session/', views.book_session, name='book_session'),
    path('booking_list/', views.booking_list, name='booking_list'),

    path('notifications/', views.notifications, name='notifications'),

    path('create_meeting/', views.create_meeting, name='create_meeting'),
]
