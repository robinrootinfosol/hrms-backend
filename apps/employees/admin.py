from django.contrib import admin
from employees.models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('get_employee_id', 'get_full_name', 'designation', 'gender', 'date_of_joining')
    list_filter = ('gender', 'designation')
    search_fields = ('user__email', 'user__employee_id', 'user__first_name', 'user__last_name')

    @admin.display(description='Employee ID')
    def get_employee_id(self, obj):
        return obj.user.employee_id

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.full_name