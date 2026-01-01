from django.urls import path
from . import views
from . import admin_views
from . import admin_workflow_views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('home/', views.home, name='home'),
    path('awareness/', views.awareness, name='awareness'),
    path('faq/', views.faq, name='faq'),
    path('profile/', views.profile, name='profile'),
    
    # Admin User Management
    path('admin/users/', admin_views.UserListView.as_view(), name='user_list'),
    path('admin/users/new/', admin_views.UserCreateView.as_view(), name='user_create'),
    path('admin/users/<int:pk>/edit/', admin_views.UserUpdateView.as_view(), name='user_update'),
    path('admin/users/<int:pk>/delete/', admin_views.UserDeleteView.as_view(), name='user_delete'),

    # Admin Workflow (Orgs, etc)
    path('admin/org-approvals/', admin_workflow_views.OrganizationApprovalListView.as_view(), name='admin_org_approvals'),
    path('admin/org-approvals/<int:org_id>/action/', admin_workflow_views.ApproveOrganizationView.as_view(), name='admin_org_action'),
    path('admin/audit-logs/', admin_workflow_views.AuditLogExplorerView.as_view(), name='admin_audit_logs'),

    # Admin Case Management
    path('admin/cases/', admin_views.AdminCaseListView.as_view(), name='admin_case_list'),
    path('admin/cases/<int:pk>/manage/', admin_views.AdminCaseUpdateView.as_view(), name='admin_case_update'),
    path('admin/cases/<int:pk>/delete/', admin_views.AdminCaseDeleteView.as_view(), name='admin_case_delete'),
]
