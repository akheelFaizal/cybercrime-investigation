from django.db import models
from django.utils import timezone
from access_control.models import User
from .validators import validate_evidence_file

class CrimeReport(models.Model):
    class Category(models.TextChoices):
        PHISHING = 'PHISHING', 'Phishing'
        HACKING = 'HACKING', 'Hacking'
        FRAUD = 'FRAUD', 'Online Fraud'
        IDENTITY_THEFT = 'IDENTITY_THEFT', 'Identity Theft'
        CYBERBULLYING = 'CYBERBULLYING', 'Cyberbullying'
        RANSOMWARE = 'RANSOMWARE', 'Ransomware'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        ASSIGNED = 'ASSIGNED', 'Assigned to Officer'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
        REJECTED = 'REJECTED', 'Rejected'

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=Category.choices)
    description = models.TextField()
    incident_date = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    is_escalated = models.BooleanField(default=False)
    
    reporter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='filed_reports'
    )
    
    assigned_officer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_cases',
        limit_choices_to={'role': User.Role.OFFICER}
    )

    def __str__(self):
        return f"{self.get_category_display()} - {self.title} (#{self.id})"

class Evidence(models.Model):
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='evidences')
    file = models.FileField(upload_to='evidence/%Y/%m/%d/', validators=[validate_evidence_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Evidence for Report #{self.report.id}"

class InvestigationNote(models.Model):
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='notes')
    officer = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.officer.username} on Report #{self.report.id}"

class CaseStatusHistory(models.Model):
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=CrimeReport.Status.choices, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=CrimeReport.Status.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status change for #{self.report.id}: {self.previous_status} -> {self.new_status}"
