from .models import Notification

def send_notification(recipient, message, link=None, notification_type=Notification.Type.INFO, sender=None):
    """
    Utility to create a notification for a user.
    """
    Notification.objects.create(
        recipient=recipient,
        message=message,
        link=link,
        notification_type=notification_type,
        sender=sender
    )
