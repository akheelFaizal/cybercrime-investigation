from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import CrimeReport, InvestigationNote, CaseStatusHistory
from actions.models import AuditLog
from actions.utils import send_notification
from access_control.models import User

@receiver(pre_save, sender=CrimeReport)
def capture_previous_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CrimeReport.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_assigned_officer = old_instance.assigned_officer
        except CrimeReport.DoesNotExist:
            instance._old_status = None
            instance._old_assigned_officer = None
    else:
        instance._old_status = None
        instance._old_assigned_officer = None

@receiver(post_save, sender=CrimeReport)
def handle_report_changes(sender, instance, created, **kwargs):
    if created:
        # 1. Log Creation
        AuditLog.objects.create(
            user=instance.reporter,
            action=f"Created report #{instance.id}",
            details=f"Title: {instance.title}"
        )
        # 2. Notify Org Admin if reporter is staff
        org = instance.reporter.get_organization()
        if org and instance.reporter != org.user:
            send_notification(
                recipient=org.user,
                message=f"New report submitted by staff: {instance.reporter.get_full_name()}",
                link=f"/reporting/{instance.id}/",
                notification_type='INFO'
            )
    else:
        # Check for status change
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            # Log History
            CaseStatusHistory.objects.create(
                report=instance,
                previous_status=old_status,
                new_status=instance.status,
                remarks=f"Status changed from {old_status} to {instance.status}"
            )
            # Notify Reporter
            send_notification(
                recipient=instance.reporter,
                message=f"Case #{instance.id} status changed to {instance.get_status_display()}",
                link=f"/reporting/{instance.id}/",
                notification_type='SUCCESS'
            )
        
        # Check for assignment change
        old_officer = getattr(instance, '_old_assigned_officer', None)
        if instance.assigned_officer and instance.assigned_officer != old_officer:
            # Notify Officer
            send_notification(
                recipient=instance.assigned_officer,
                message=f"You have been assigned to Case #{instance.id}",
                link=f"/reporting/{instance.id}/",
                notification_type='ALERT'
            )
            # Notify Reporter
            send_notification(
                recipient=instance.reporter,
                message=f"An investigator has been assigned to your case #{instance.id}",
                link=f"/reporting/{instance.id}/",
            )

@receiver(post_save, sender=InvestigationNote)
def notify_note_added(sender, instance, created, **kwargs):
    if created:
        report = instance.report
        # Notify reporter
        send_notification(
            recipient=report.reporter,
            message=f"New update/note on your case #{report.id}",
            link=f"/reporting/{report.id}/"
        )

