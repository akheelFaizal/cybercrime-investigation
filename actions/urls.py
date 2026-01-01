from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    path('notifications/read/all/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]
