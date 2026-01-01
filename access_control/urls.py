from django.urls import path
from . import views
from . import staff_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('register/citizen/', views.register_citizen, name='register_citizen'),
    path('register/organization/', views.register_org, name='register_org'),
    
    # Organization Staff Management
    path('staff/', staff_views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', staff_views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/delete/', staff_views.StaffDeleteView.as_view(), name='staff_delete'),
]
