from django.urls import path
from employees.views import EmployeeRegisterView

urlpatterns = [
    path('register/',EmployeeRegisterView.as_view(),name='emaployee-register'),
]
