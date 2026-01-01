from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, OrganizationProfile, OfficerProfile

class CitizenRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CITIZEN
        if commit:
            user.save()
        return user

class OrganizationRegistrationForm(UserCreationForm):
    organization_name = forms.CharField(max_length=255)
    registration_number = forms.CharField(max_length=100)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.ORGANIZATION
        user.org_role = User.OrgRole.ADMIN
        if commit:
            user.save()
            OrganizationProfile.objects.create(
                user=user,
                organization_name=self.cleaned_data['organization_name'],
                registration_number=self.cleaned_data['registration_number']
            )
        return user
