from django.db.models.signals import post_save
from django.dispatch import receiver
from access_control.models import User
from .models import Notification, AuditLog
from .utils import send_notification

@receiver(post_save, sender=User)
def welcome_notification(sender, instance, created, **kwargs):
    if created:
        if instance.is_organization() and instance.organization:
            # This is a staff member
            send_notification(
                recipient=instance,
                message=f"Welcome to {instance.organization.organization_name}! Your role is {instance.get_org_role_display()}.",
                link="/dashboard/",
                notification_type=Notification.Type.SUCCESS
            )
            
        AuditLog.objects.create(
            user=instance,
            action="User Created",
            details=f"User {instance.username} created with role {instance.role}."
        )
