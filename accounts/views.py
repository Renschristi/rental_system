"""
Authentication Views
"""
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .forms import UserRegistrationForm


class RegisterView(View):
    """User registration"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboards:home')
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboards:home')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    """User login"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboards:home')
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboards:home')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    """User logout"""
    
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')
