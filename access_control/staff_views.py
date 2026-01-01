from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from .models import User, OrganizationProfile
from .forms import CitizenRegistrationForm # Reuse generic form for now, simplify
from django import forms
from django.contrib.auth.hashers import make_password

class OrgRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_organization() and hasattr(self.request.user, 'org_profile')

class StaffListView(OrgRequiredMixin, ListView):
    model = User
    template_name = 'access_control/staff_list.html'
    context_object_name = 'staff_members'

    def get_queryset(self):
        # Return users linked to this org
        return User.objects.filter(organization=self.request.user.org_profile).exclude(id=self.request.user.id)

class StaffCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Set Role to Organization (Staff) or maybe CITIZEN? 
        # Requirement says "Staff under organization". Usually implied they act ON BEHALF of org.
        # Let's keep them as ORGANIZATION role for permissions, but they aren't the primary owner.
        user.role = User.Role.ORGANIZATION 
        if commit:
            user.save()
        return user

class StaffCreateView(OrgRequiredMixin, CreateView):
    model = User
    form_class = StaffCreateForm
    template_name = 'access_control/staff_form.html'
    success_url = reverse_lazy('staff_list')

    def form_valid(self, form):
        form.instance.organization = self.request.user.org_profile
        form.instance.is_active = True
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = "Add New Staff Member"
        return ctx

class StaffDeleteView(OrgRequiredMixin, DeleteView):
    model = User
    template_name = 'access_control/staff_confirm_delete.html'
    success_url = reverse_lazy('staff_list')
    
    def get_queryset(self):
        # Ensure org can only delete their own staff
        return User.objects.filter(organization=self.request.user.org_profile)
