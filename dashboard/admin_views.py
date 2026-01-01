from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from access_control.models import User
from access_control.forms import CitizenRegistrationForm
from reporting.models import CrimeReport
from reporting.forms import CrimeReportForm # Or create a specific form for assignment
from django import forms

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = CitizenRegistrationForm # Reuse for simplicity or create AdminUserCreationForm
    template_name = 'dashboard/admin/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        return context

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'role', 'is_active']
    template_name = 'dashboard/admin/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update User'
        return context

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

# --- Case Management ---

class AdminCaseListView(AdminRequiredMixin, ListView):
    model = CrimeReport
    template_name = 'dashboard/admin/case_list.html'
    context_object_name = 'cases'
    paginate_by = 20
    
    def get_queryset(self):
        qs = CrimeReport.objects.all().order_by('-reported_at')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

class CaseAssignmentForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ['assigned_officer', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter queryset to show only Officers
        self.fields['assigned_officer'].queryset = User.objects.filter(role=User.Role.OFFICER)
        self.fields['assigned_officer'].label = "Assign to Officer"

class AdminCaseUpdateView(AdminRequiredMixin, UpdateView):
    model = CrimeReport
    form_class = CaseAssignmentForm
    template_name = 'dashboard/admin/case_form.html'
    success_url = reverse_lazy('admin_case_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Manage Case #{self.object.id}'
        return context
class AdminCaseDeleteView(AdminRequiredMixin, DeleteView):
    model = CrimeReport
    template_name = 'dashboard/admin/case_confirm_delete.html'
    success_url = reverse_lazy('admin_case_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Case #{self.object.id}'
        return context
