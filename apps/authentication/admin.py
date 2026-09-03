from django.contrib import admin
from authentication.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'email', 'full_name', 'role', 'is_active', 'is_staff')
    list_display_links = ('employee_id', 'email')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'employee_id', 'first_name', 'last_name', 'phone_number')
    ordering = ('-id',)
    
    readonly_fields = ('employee_id',)

    fieldsets = (
        ('System Identification', {
            'fields': ('employee_id',)
        }),
        ('Credentials & Personal Info', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )