from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from .models import User, OrganizationProfile
from django import forms
from django.contrib.auth.hashers import make_password

class OrgAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (user.is_authenticated and 
                user.is_organization() and 
                user.org_role == User.OrgRole.ADMIN and 
                hasattr(user, 'org_profile'))

class StaffListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'access_control/staff_list.html'
    context_object_name = 'staff_members'

    def get_queryset(self):
        org = self.request.user.get_organization()
        if not org:
            return User.objects.none()
        # Return users linked to this org, exclude the primary user if it's the one viewing
        return User.objects.filter(organization=org).exclude(id=org.user.id)

class StaffCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'org_role', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.ORGANIZATION 
        if commit:
            user.save()
        return user

class StaffUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'org_role', 'is_active']

class StaffCreateView(OrgAdminRequiredMixin, CreateView):
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

class StaffUpdateView(OrgAdminRequiredMixin, UpdateView):
    model = User
    form_class = StaffUpdateForm
    template_name = 'access_control/staff_form.html'
    success_url = reverse_lazy('staff_list')

    def get_queryset(self):
        return User.objects.filter(organization=self.request.user.org_profile)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = "Update Staff Member"
        return ctx

class StaffDeleteView(OrgAdminRequiredMixin, DeleteView):
    model = User
    template_name = 'access_control/staff_confirm_delete.html'
    success_url = reverse_lazy('staff_list')
    
    def get_queryset(self):
        return User.objects.filter(organization=self.request.user.org_profile)
