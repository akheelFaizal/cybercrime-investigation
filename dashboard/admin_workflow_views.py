from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.contrib import messages
from access_control.models import OrganizationProfile, User
from actions.utils import send_notification
from actions.models import Notification, AuditLog

class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class OrganizationApprovalListView(AdminRequiredMixin, ListView):
    model = OrganizationProfile
    template_name = 'dashboard/admin/org_approvals.html'
    context_object_name = 'pending_orgs'

    def get_queryset(self):
        return OrganizationProfile.objects.filter(is_approved=False).order_by('-id')

class ApproveOrganizationView(AdminRequiredMixin, View):
    def post(self, request, org_id):
        org = get_object_or_404(OrganizationProfile, id=org_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            org.is_approved = True
            org.save()
            
            # Notify the org admin
            send_notification(
                recipient=org.user,
                message=f"Your organization {org.organization_name} has been approved. You can now access the full dashboard.",
                link='/dashboard/',
                notification_type=Notification.Type.SUCCESS
            )
            messages.success(request, f"Organization {org.organization_name} approved successfully.")
            
        elif action == 'reject':
            # Optionally delete or just mark as rejected if we add a status field
            # For now, let's just show how we'd handle it
            messages.warning(request, f"Organization {org.organization_name} registration rejected.")
            
        return redirect('admin_org_approvals')

class AuditLogExplorerView(AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = 'dashboard/admin/audit_logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by('-timestamp')
        user_id = self.request.GET.get('user')
        action = self.request.GET.get('action')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action__icontains=action)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For filtering dropdowns
        context['users'] = User.objects.filter(role__in=['ADMIN', 'OFFICER'])
        return context
