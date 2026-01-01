from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CrimeReport

@login_required
def investigation_summary(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id)
    
    # Access control: Only assigned officer or admin
    if request.user != report.assigned_officer and not request.user.is_admin():
        return render(request, '403_access_denied.html')

    context = {
        'report': report,
        'notes': report.notes.all().order_by('created_at'),
        'evidence': report.evidences.all()
    }
    return render(request, 'reporting/investigation_summary.html', context)
