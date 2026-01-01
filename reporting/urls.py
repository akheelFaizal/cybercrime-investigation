from django.urls import path
from . import views
from . import export_views
from . import pdf_views

urlpatterns = [
    path('new/', views.report_crime, name='report_crime'),
    path('mine/', views.my_reports, name='my_reports'),
    path('cases/', views.assigned_cases, name='assigned_cases'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/summary/', pdf_views.investigation_summary, name='investigation_summary'),
    path('export/', export_views.export_reports, name='export_reports'),
]
