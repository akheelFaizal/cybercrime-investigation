from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CrimeReport, InvestigationNote
from actions.models import Notification, AuditLog
from access_control.models import User

@receiver(post_save, sender=CrimeReport)
def notify_report_update(sender, instance, created, **kwargs):
    """
    Notify reporter when status changes.
    Notify officers when a new case is assigned (or pending if logic requires).
    """
    if created:
        # Notify Admins/Officers of new high-priority report?
        # For now, just log audit
        AuditLog.objects.create(
            user=instance.reporter,
            action=f"Created report #{instance.id}: {instance.title}",
            details=f"Category: {instance.category}"
        )
    else:
        # Status Change Notification to Reporter
        # Check if status changed? We don't have previous state here easily without custom dirty fields logic or pre_save.
        # But assuming save() is called often only on changes.
        Notification.objects.create(
            recipient=instance.reporter,
            message=f"Your report #{instance.id} status is now: {instance.get_status_display()}",
            link=f"/reporting/{instance.id}/"
        )
        
        # Assignment Notification
        if instance.assigned_officer:
            Notification.objects.create(
                recipient=instance.assigned_officer,
                message=f"You have been assigned case #{instance.id}",
                link=f"/reporting/{instance.id}/"
            )
            
        AuditLog.objects.create(
            action=f"Report #{instance.id} updated",
            details=f"Status: {instance.status}"
        )

@receiver(post_save, sender=InvestigationNote)
def notify_note_added(sender, instance, created, **kwargs):
    if created:
        report = instance.report
        # Notify reporter that an update/note was added? Usually internal unless public.
        # Let's assume notes are internal or visible to user.
        # If visible:
        Notification.objects.create(
            recipient=report.reporter,
            message=f"New update on report #{report.id}",
            link=f"/reporting/{report.id}/"
        )
