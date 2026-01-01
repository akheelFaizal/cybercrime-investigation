from .models import AuditLog

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log authenticated actions that are not GET requests (unsafe methods)
        if request.user.is_authenticated and request.method not in ['GET', 'HEAD', 'OPTIONS']:
            ip = self.get_client_ip(request)
            AuditLog.objects.create(
                user=request.user,
                action=f"{request.method} {request.path}",
                ip_address=ip,
                details=str(request.POST.dict())[:500] # Log truncated POST data (be careful with passwords)
            )
            
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
