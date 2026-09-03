from django.db import models
import os
from django.conf import settings
from common.models import BaseModel
from organization.models import Designation


def employee_profile_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"profiles/{instance.user.employee_id}/avatar{ext}"

class EmployeeProfile(BaseModel):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.RESTRICT,
        related_name='employees'
    )
    dob = models.DateField()
    gender = models.CharField(max_length=10,choices=Gender.choices)
    date_of_joining = models.DateField()
    profile_picture = models.ImageField(upload_to=employee_profile_upload_path)

    class Meta:
        db_table = 'hrms_employee_profiles'

    def __str__(self):
        return f"{self.user.full_name} - {self.designation.name}"
