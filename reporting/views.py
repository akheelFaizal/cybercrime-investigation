from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CrimeReport, Evidence, InvestigationNote
from .forms import CrimeReportForm

@login_required
def report_crime(request):
    if request.method == 'POST':
        form = CrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            
            # Handle multiple evidence files
            files = request.FILES.getlist('evidence')
            from .validators import validate_evidence_file
            from django.core.exceptions import ValidationError
            from django.contrib import messages
            
            valid_files_count = 0
            for f in files:
                try:
                    validate_evidence_file(f)
                    Evidence.objects.create(report=report, file=f)
                    valid_files_count += 1
                except ValidationError as e:
                    messages.warning(request, f"Skipped file {f.name}: {e.message}")
            
            if len(files) > 0 and valid_files_count == 0:
                 messages.error(request, "No valid evidence files were uploaded.")
            elif valid_files_count > 0:
                 messages.success(request, f"Report submitted with {valid_files_count} evidence files.")
            else:
                 messages.success(request, "Report submitted successfully.")

            return redirect('my_reports')
    else:
        form = CrimeReportForm()
    return render(request, 'reporting/report_form.html', {'form': form})

@login_required
def my_reports(request):
    reports = CrimeReport.objects.filter(reporter=request.user).order_by('-reported_at')
    return render(request, 'reporting/my_reports.html', {'reports': reports})

@login_required
def assigned_cases(request):
    # For officers
    cases = CrimeReport.objects.filter(assigned_officer=request.user)
    return render(request, 'reporting/assigned_cases.html', {'cases': cases})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id)
    
    # Access control: Reporter OR Assigned Officer OR Admin
    if request.user != report.reporter and request.user != report.assigned_officer and not request.user.is_admin():
        return render(request, '403_access_denied.html') # Or redirect with error

    # Filter notes: Everyone sees public notes, only officers/admins see internal notes
    if request.user.is_officer() or request.user.is_admin():
        notes = report.notes.all().order_by('-created_at')
    else:
        notes = report.notes.filter(is_internal=False).order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_officer():
        new_status = request.POST.get('status')
        new_note = request.POST.get('note')
        is_internal = request.POST.get('is_internal') == 'on'
        source_url = request.POST.get('source_url')
        severity = request.POST.get('severity')
        
        if new_status:
            report.status = new_status
            report.save()
            
        if severity:
            report.severity = severity
            report.save()
        
        if new_note:
            InvestigationNote.objects.create(
                report=report,
                officer=request.user,
                note=new_note,
                is_internal=is_internal
            )
            
        if source_url:
            Evidence.objects.create(
                report=report,
                source_url=source_url,
                is_investigator_added=True,
                description=f"Automated reference added by {request.user.username}"
            )
            
        return redirect('report_detail', report_id=report.id)

    return render(request, 'reporting/report_detail.html', {'report': report, 'notes': notes})

@login_required
def submit_followup(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id, reporter=request.user)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        files = request.FILES.getlist('evidence')
        source_url = request.POST.get('source_url')
        
        from .validators import validate_evidence_file
        from django.contrib import messages
        
        if source_url:
             Evidence.objects.create(report=report, source_url=source_url, description=description)
             messages.success(request, "Link added to evidence.")

        for f in files:
            try:
                validate_evidence_file(f)
                Evidence.objects.create(report=report, file=f, description=description)
            except Exception as e:
                messages.warning(request, f"Error with file {f.name}: {e}")
        
        if not files and not source_url:
            messages.error(request, "Please provide a file or a link.")
            
        return redirect('report_detail', report_id=report.id)
    
    return render(request, 'reporting/followup_evidence.html', {'report': report})

@login_required
def request_escalation(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id, reporter=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        report.is_escalated = True
        report.save()
        
        # Log to history
        from .models import CaseStatusHistory
        CaseStatusHistory.objects.create(
            report=report,
            previous_status=report.status,
            new_status=report.status, # Status doesn't change, just escalation flag
            changed_by=request.user,
            remarks=f"ESCALATION REQUESTED: {reason}"
        )
        
        # Notify Admins
        from actions.utils import send_notification
        from actions.models import Notification
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            send_notification(
                recipient=admin,
                message=f"Urgent: Escalation requested for Case #{report.id}",
                link=f"/reporting/{report.id}/",
                notification_type=Notification.Type.WARNING,
                sender=request.user
            )

        from django.contrib import messages
        messages.success(request, "Escalation request submitted for review.")
        return redirect('report_detail', report_id=report.id)
    
    return render(request, 'reporting/request_escalation.html', {'report': report})
