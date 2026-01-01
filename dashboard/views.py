from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from reporting.models import CrimeReport

def home(request):
    return render(request, 'home.html')

def awareness(request):
    return render(request, 'dashboard/awareness.html')

def faq(request):
    return render(request, 'dashboard/faq.html')

@login_required
def profile(request):
    return render(request, 'dashboard/profile.html')

@login_required
def dashboard_view(request):
    user = request.user
    context = {}
    
    if user.is_citizen():
        reports = CrimeReport.objects.filter(reporter=user).order_by('-reported_at')[:5]
        context = {'reports': reports, 'role': 'Citizen'}
        return render(request, 'dashboard/citizen_dashboard.html', context)
        
    elif user.is_organization():
        reports = CrimeReport.objects.filter(reporter=user).order_by('-reported_at')
        context = {'reports': reports, 'role': 'Organization'}
        return render(request, 'dashboard/org_dashboard.html', context)
        
    elif user.is_officer():
        cases = CrimeReport.objects.filter(assigned_officer=user).exclude(status=CrimeReport.Status.CLOSED)
        context = {'cases': cases, 'role': 'Officer'}
        return render(request, 'dashboard/officer_dashboard.html', context)
        
    elif user.is_admin():
        from actions.models import AuditLog
        from django.db.models import Count
        import json
        
        # Key Stats
        total_reports = CrimeReport.objects.count()
        # Pending: Status is PENDING
        pending = CrimeReport.objects.filter(status=CrimeReport.Status.PENDING).count()
        # Assigned: Has an officer assigned
        assigned_count = CrimeReport.objects.filter(assigned_officer__isnull=False).count()
        # Unassigned: No officer
        unassigned_count = CrimeReport.objects.filter(assigned_officer__isnull=True).count()
        
        # Chart Data: Reports per status
        status_counts = list(CrimeReport.objects.values('status').annotate(count=Count('status')))
        labels = [item['status'] for item in status_counts]
        data = [item['count'] for item in status_counts]
        
        # Chart 2: Assignment (Keep as is)
        distribution_labels = ['Assigned', 'Unassigned']
        distribution_data = [assigned_count, unassigned_count]

        # Chart 3: Reports by Category
        category_counts = list(CrimeReport.objects.values('category').annotate(count=Count('category')))
        # Displayable labels for category choices?
        # Need to map values to display names.
        cat_map = dict(CrimeReport.Category.choices)
        cat_labels = [cat_map.get(item['category'], item['category']) for item in category_counts]
        cat_data = [item['count'] for item in category_counts]

        # Chart 4: Monthly Trends (Last 6 months)
        from django.db.models.functions import TruncMonth
        import datetime
        from django.utils import timezone
        
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        trends = CrimeReport.objects.filter(reported_at__gte=six_months_ago)\
            .annotate(month=TruncMonth('reported_at'))\
            .values('month')\
            .annotate(count=Count('id'))\
            .order_by('month')
            
        trend_labels = [item['month'].strftime("%b %Y") for item in trends]
        trend_data = [item['count'] for item in trends]
        
        # Audit Logs (Recent System Activity)
        recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
        
        context = {
            'total_reports': total_reports, 
            'pending_cases': pending,
            'assigned_cases': assigned_count,
            'role': 'Administrator',
            'chart_labels': labels,
            'chart_data': data,
            'dist_labels': distribution_labels,
            'dist_data': distribution_data,
            'cat_labels': cat_labels,
            'cat_data': cat_data,
            'trend_labels': trend_labels,
            'trend_data': trend_data,
            'recent_logs': recent_logs
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    return render(request, 'dashboard/general.html', context)
