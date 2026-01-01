from django.urls import path
from . import views
from . import export_views
from . import investigator_views

urlpatterns = [
    path('new/', views.report_crime, name='report_crime'),
    path('mine/', views.my_reports, name='my_reports'),
    path('cases/', investigator_views.InvestigatorDashboardView.as_view(), name='assigned_cases'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/followup/', views.submit_followup, name='submit_followup'),
    path('<int:report_id>/escalate/', views.request_escalation, name='request_escalation'),
    path('<int:pk>/summary/', investigator_views.InvestigationSummaryView.as_view(), name='investigation_summary'),
    path('export/', export_views.export_reports, name='export_reports'),
]
