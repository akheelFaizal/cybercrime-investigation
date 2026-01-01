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

    notes = report.notes.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_officer():
        # Handle updating status or adding notes
        new_status = request.POST.get('status')
        new_note = request.POST.get('note')
        
        if new_status:
            report.status = new_status
            report.save()
        
        if new_note:
            InvestigationNote.objects.create(
                report=report,
                officer=request.user,
                note=new_note
            )
        return redirect('report_detail', report_id=report.id)

    return render(request, 'reporting/report_detail.html', {'report': report, 'notes': notes})
