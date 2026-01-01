from django.contrib import admin
from .models import CrimeReport, Evidence, InvestigationNote

class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0

class NoteInline(admin.TabularInline):
    model = InvestigationNote
    extra = 0

@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'reporter', 'assigned_officer', 'reported_at')
    list_filter = ('category', 'status', 'reported_at')
    search_fields = ('title', 'description', 'reporter__username')
    inlines = [EvidenceInline, NoteInline]

admin.site.register(Evidence)
admin.site.register(InvestigationNote)
