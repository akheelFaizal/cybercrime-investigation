import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CrimeReport

@login_required
def export_reports(request):
    if not request.user.is_organization() and not request.user.is_admin():
        return render(request, '403_access_denied.html')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crime_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Category', 'Date', 'Status'])

    reports = CrimeReport.objects.filter(reporter=request.user)
    if request.user.is_admin():
        reports = CrimeReport.objects.all()

    for report in reports:
        writer.writerow([
            report.id, 
            report.title, 
            report.get_category_display(), 
            report.incident_date, 
            report.get_status_display()
        ])

    return response
