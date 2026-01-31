from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import SystemSettings
from .forms import SystemSettingsForm


def is_staff(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff)
def settings_view(request):
    """View and edit system settings (Admin only)"""
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('system_config:settings')
    else:
        form = SystemSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'system_config/settings.html', context)
