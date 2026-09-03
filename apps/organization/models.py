from django.db import models
from common.models import BaseModel

class Department(BaseModel):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'hrms_departments'
        ordering = ['name']

    def __str__(self):
        return self.name

class Designation(BaseModel):
    name = models.CharField(max_length=100,unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='designations'
    )
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'hrms_designations'
        ordering = ['name']

    def __str__(self):
        return self.name
