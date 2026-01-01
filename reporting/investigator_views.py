from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.db.models import Count, Avg, F
from .models import CrimeReport, InvestigationNote, Evidence
from access_control.models import User

class InvestigatorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_officer():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class InvestigatorDashboardView(InvestigatorRequiredMixin, ListView):
    model = CrimeReport
    template_name = 'reporting/investigator/dashboard.html'
    context_object_name = 'assigned_cases'

    def get_queryset(self):
        from datetime import timedelta
        from django.utils import timezone
        overdue_threshold = timezone.now() - timedelta(days=7)
        
        return CrimeReport.objects.filter(
            assigned_officer=self.request.user
        ).annotate(
            is_overdue=models.Case(
                models.When(reported_at__lt=overdue_threshold, status__in=['PENDING', 'ASSIGNED'], then=True),
                default=False,
                output_field=models.BooleanField(),
            )
        ).order_by('-priority', '-is_overdue', '-reported_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Performance Metrics
        all_cases = CrimeReport.objects.filter(assigned_officer=user)
        context['total_assigned'] = all_cases.count()
        context['active_cases'] = all_cases.exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()
        context['resolved_cases'] = all_cases.filter(status='RESOLVED').count()
        
        # Avg resolution time for this officer
        avg_time = all_cases.filter(status='RESOLVED').annotate(
            duration=F('updated_at') - F('reported_at')
        ).aggregate(Avg('duration'))['duration__avg']
        
        context['avg_res_time'] = f"{avg_time.days}d {avg_time.seconds // 3600}h" if avg_time else "N/A"
        
        # New reports (unassigned globally) to show potential cases? 
        # Or just show urgent assigned ones
        context['urgent_cases'] = all_cases.filter(priority='CRITICAL').exclude(status='CLOSED')
        
        return context

class InvestigationSummaryView(InvestigatorRequiredMixin, DetailView):
    model = CrimeReport
    template_name = 'reporting/investigator/investigation_summary.html'
    context_object_name = 'report'

    def get_queryset(self):
        # Ensure they can only see summaries for assigned cases or if they are admin
        if self.request.user.is_admin():
            return CrimeReport.objects.all()
        return CrimeReport.objects.filter(assigned_officer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Gather all evidence, notes, and history
        context['notes'] = self.object.notes.all().order_by('created_at')
        context['evidence'] = self.object.evidences.all()
        context['history'] = self.object.status_history.all().order_by('timestamp')
        return context
