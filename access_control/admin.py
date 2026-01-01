from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OrganizationProfile, OfficerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'phone_number', 'address')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(OrganizationProfile)
admin.site.register(OfficerProfile)
