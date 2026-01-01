from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CitizenRegistrationForm, OrganizationRegistrationForm

def register(request):
    return render(request, 'access_control/register_landing.html')

def register_citizen(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'access_control/register.html', {'form': form, 'title': 'Citizen Registration'})

def register_org(request):
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = OrganizationRegistrationForm()
    return render(request, 'access_control/register.html', {'form': form, 'title': 'Organization Registration'})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'access_control/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
