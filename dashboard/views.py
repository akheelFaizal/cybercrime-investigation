from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from reporting.models import CrimeReport
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

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
        reports = CrimeReport.objects.filter(reporter=user).order_by('-reported_at')
        from actions.models import Notification
        recent_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
        context = {
            'reports': reports[:5], 
            'total_reports': reports.count(),
            'resolved_reports': reports.filter(status__in=['RESOLVED', 'CLOSED']).count(),
            'recent_notifications': recent_notifications,
            'role': 'Citizen'
        }
        return render(request, 'dashboard/citizen_dashboard.html', context)
        
    elif user.is_organization():
        org = user.get_organization()
        if org and not org.is_approved:
            return render(request, 'dashboard/org_pending.html', {'org': org})
            
        # Organization Stats
        if org:
            from django.db.models import Count
            from django.db.models.functions import TruncMonth
            import datetime
            from django.utils import timezone

            # Primary Org User + all staff members
            users_in_org = User.objects.filter(models.Q(organization=org) | models.Q(id=org.user.id))
            all_reports = CrimeReport.objects.filter(reporter__in=users_in_org).order_by('-reported_at')
            
            # Stats
            total = all_reports.count()
            pending = all_reports.filter(status='PENDING').count()
            resolved = all_reports.filter(status__in=['RESOLVED', 'CLOSED']).count()
            
            # Trends (Last 6 months)
            six_months_ago = timezone.now() - datetime.timedelta(days=180)
            trends = all_reports.filter(reported_at__gte=six_months_ago)\
                .annotate(month=TruncMonth('reported_at'))\
                .values('month')\
                .annotate(count=Count('id'))\
                .order_by('month')
            
            trend_labels = [item['month'].strftime("%b %Y") for item in trends]
            trend_data = [item['count'] for item in trends]

            context = {
                'reports': all_reports[:10], # Recent reports
                'total_cases': total,
                'pending_cases': pending,
                'resolved_cases': resolved,
                'trend_labels': trend_labels,
                'trend_data': trend_data,
                'role': 'Organization Staff' if user.org_role == User.OrgRole.STAFF else 'Organization Admin',
                'organization': org
            }
        else:
            context = {'reports': CrimeReport.objects.none(), 'role': 'Organization'}
        return render(request, 'dashboard/org_dashboard.html', context)
        
    elif user.is_officer():
        cases = CrimeReport.objects.filter(assigned_officer=user).exclude(status=CrimeReport.Status.CLOSED)
        context = {'cases': cases, 'role': 'Officer'}
        return render(request, 'dashboard/officer_dashboard.html', context)
        
    elif user.is_admin():
        from actions.models import AuditLog
        from django.db.models import Count, Avg, F
        import json
        
        # Key Stats
        total_reports = CrimeReport.objects.count()
        pending = CrimeReport.objects.filter(status=CrimeReport.Status.PENDING).count()
        active_cases = CrimeReport.objects.filter(status__in=['UNDER_REVIEW', 'ASSIGNED']).count()
        resolved_cases = CrimeReport.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()
        
        # SLA: Average time to resolve (Assumes RESOLVED status implies completion)
        # Simplified: diff between reported_at and updated_at for resolved cases
        avg_res_time = CrimeReport.objects.filter(status='RESOLVED').annotate(
            duration=F('updated_at') - F('reported_at')
        ).aggregate(Avg('duration'))['duration__avg']
        
        # Convert duration to hours/days for display
        avg_res_display = f"{avg_res_time.days}d {avg_res_time.seconds // 3600}h" if avg_res_time else "N/A"

        unassigned_count = CrimeReport.objects.filter(assigned_officer__isnull=True).count()
        assigned_count = total_reports - unassigned_count
        
        # Chart Data: Reports per status
        status_counts = list(CrimeReport.objects.values('status').annotate(count=Count('status')))
        labels = [dict(CrimeReport.Status.choices).get(item['status'], item['status']) for item in status_counts]
        data = [item['count'] for item in status_counts]
        
        # Chart 2: Assignment
        distribution_labels = ['Assigned', 'Unassigned']
        distribution_data = [assigned_count, unassigned_count]

        # Chart 3: Reports by Category
        category_counts = list(CrimeReport.objects.values('category').annotate(count=Count('category')))
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
        
        # Performance: Cases per officer
        officer_stats = User.objects.filter(role=User.Role.OFFICER).annotate(
            case_count=Count('assigned_cases')
        ).order_by('-case_count')[:5]

        # Unassigned cases for the "Assignment Panel"
        unassigned_cases = CrimeReport.objects.filter(assigned_officer__isnull=True).order_by('-reported_at')[:5]

        # Per-Organization Metrics
        from access_control.models import OrganizationProfile
        org_stats = OrganizationProfile.objects.annotate(
            total_cases=Count('user__filed_reports'),
            resolved_cases=Count('user__filed_reports', filter=models.Q(user__filed_reports__status='RESOLVED')),
        ).filter(total_cases__gt=0).order_by('-total_cases')[:5]

        context = {
            'role': 'Admin',
            'total_reports': total_reports,
            'pending': pending,
            'active_cases': active_cases,
            'resolved_cases': resolved_cases,
            'avg_res_time': avg_res_display,
            'status_labels': json.dumps(labels),
            'status_data': json.dumps(data),
            'cat_labels': json.dumps(cat_labels),
            'cat_data': json.dumps(cat_data),
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_logs': AuditLog.objects.all().order_by('-timestamp')[:5],
            'urgent_reports': CrimeReport.objects.filter(assigned_officer__isnull=True).order_by('-priority')[:5],
            'officer_workload': User.objects.filter(role=User.Role.OFFICER).annotate(case_count=Count('assigned_cases')).order_by('-case_count')[:5],
            'org_performance': org_stats
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    return render(request, 'dashboard/general.html', context)
