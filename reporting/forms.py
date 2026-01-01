from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import CrimeReport, Evidence

class CrimeReportForm(forms.ModelForm):
    incident_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label='Date and Time of Incident'
    )
    
    
    class Meta:
        model = CrimeReport
        fields = ['title', 'category', 'description', 'incident_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_incident_date(self):
        date = self.cleaned_data['incident_date']
        if date > timezone.now():
            raise ValidationError("Incident date cannot be in the future.")
        return date

    def clean_evidence(self):
        # Note: This is usually handled in the view for multiple files if not using a custom field
        pass
