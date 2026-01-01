from django.db.models.signals import post_save
from django.dispatch import receiver
from reporting.models import CrimeReport
from .models import Notification

@receiver(post_save, sender=CrimeReport)
def notify_status_change(sender, instance, created, **kwargs):
    from .models import AuditLog # Import here to avoid circular dependency
    
    if created:
        # Log Creation
        AuditLog.objects.create(
            user=instance.reporter,
            action="Report Created",
            details=f"New report '{instance.title}' filed by {instance.reporter.username}."
        )
        # Notify Admins (conceptually, or just leave as is)

    else:
        # Check if status changed (requires tracking previous state, but for simplicty we assume save implies update here or check pre_save.
        # Ideally, we check instance._state or use pre_save to compare. 
        # For this quick impl, we'll log general updates.
        
        action = "Report Updated"
        details = f"Report #{instance.id} updated. Current Status: {instance.get_status_display()}."
        
        # Check assignment - simplified detection
        if instance.assigned_officer:
            if instance.status == 'IN_PROGRESS' and not created: # Heuristic
                 details += f" Assigned to {instance.assigned_officer.username}."

        AuditLog.objects.create(
            user=instance.assigned_officer if instance.assigned_officer else None, # Attributing to officer if assigned, or system
            action=action,
            details=details
        )

        # Notify Reporter
        Notification.objects.create(
            recipient=instance.reporter,
            message=f"Update on Case #{instance.id}: Status is {instance.get_status_display()}",
            link=f"/reporting/{instance.id}/"
        )
        
        # Notify Assigned Officer if exists
        if instance.assigned_officer:
             Notification.objects.create(
                recipient=instance.assigned_officer,
                message=f"Case #{instance.id} update: {instance.title}",
                link=f"/reporting/{instance.id}/"
            )
