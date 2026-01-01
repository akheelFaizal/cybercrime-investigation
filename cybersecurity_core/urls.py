from django.contrib import admin
from django.urls import path, include
from dashboard.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('auth/', include('access_control.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reporting/', include('reporting.urls')),
    path('actions/', include('actions.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
