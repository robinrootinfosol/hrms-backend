import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('role',User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is)superuser=True'))

        return self.create_user(email,password,**extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        HR = 'HR', _('HR')
        MANAGER = 'MANAGER', _('Manager')
        EMPLOYEE = 'EMPLOYEE', _('Employee')       

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    employee_id = models.CharField(max_length=50,unique=True, null=True, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone_number = models.CharField(max_length=20,unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100,blank=True)
    role = models.CharField(max_length=20,choices=Role.choices,default=Role.EMPLOYEE)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_first_login = models.BooleanField(default=True)
    biometric_enable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'hrms_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email','employee_id'])
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def save(self, *args, **kwargs):
        if not self.employee_id and not self.is_superuser:
            from employees.utils import generate_employee_id
            self.employee_id = generate_employee_id()
        super().save(*args, **kwargs)
    



