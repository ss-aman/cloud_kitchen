from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_verified', 'is_active']
    list_filter = ['is_verified', 'is_active', 'verification_method']
    fieldsets = UserAdmin.fieldsets + (
        ('Verification', {'fields': ('phone_number', 'is_verified', 'verification_method')}),
    )