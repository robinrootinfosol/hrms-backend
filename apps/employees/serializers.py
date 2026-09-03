from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from organization.models import Designation
from employees.models import EmployeeProfile
from employees.utils import generate_employee_id
from authentication.utils import send_set_password_email

User = get_user_model()


class EmployeeRegisterSerializer(serializers.ModelSerializer):
    # User fields
    full_name = serializers.CharField(write_only=True, max_length=200, required=True)
    phone_number = serializers.CharField(write_only=True, max_length=20, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_null=True)

    # Profile fields
    designation = serializers.CharField(write_only=True, required=True)
    dob = serializers.DateField(write_only=True, required=True)
    gender = serializers.ChoiceField(choices=EmployeeProfile.Gender.choices, write_only=True, required=True)
    date_of_joining = serializers.DateField(write_only=True, required=True)
    profile_picture = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'email',
            'full_name',
            'phone_number',
            'password',
            'designation',
            'dob',
            'gender',
            'date_of_joining',
            'profile_picture',
        ]
        read_only_fields = ['id', 'employee_id']

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return normalized_email

    def validate_phone_number(self, value):
        cleaned_phone = value.strip()
        if User.objects.filter(phone_number=cleaned_phone).exists():
            raise serializers.ValidationError("An employee with this phone number already exists.")
        return cleaned_phone

    def validate_designation(self, value):
        cleaned_name = value.strip()
        designation_obj = Designation.objects.filter(name__iexact=cleaned_name, is_active=True).first()
        if not designation_obj:
            raise serializers.ValidationError(
                f"Designation '{cleaned_name}' does not exist or is inactive. Please choose a valid predefined designation."
            )
        # Pass the resolved model instance forward
        return designation_obj

    def create(self, validated_data):
        full_name = validated_data.pop('full_name').strip()
        phone_number = validated_data.pop('phone_number')
        # Use default=None to prevent KeyError when password is omitted
        password = validated_data.pop('password', None)
        designation = validated_data.pop('designation')
        dob = validated_data.pop('dob')
        gender = validated_data.pop('gender')
        date_of_joining = validated_data.pop('date_of_joining')
        profile_picture = validated_data.pop('profile_picture')

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        with transaction.atomic():
            employee_id = generate_employee_id()

            user = User(
                email=validated_data['email'],
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role=User.Role.EMPLOYEE,
            )

            if password:
                user.set_password(password)
                user.is_first_login = False
            else:
                user.set_unusable_password()
                user.is_first_login = True

            user.save()

            EmployeeProfile.objects.create(
                user=user,
                designation=designation,
                dob=dob,
                gender=gender,
                date_of_joining=date_of_joining,
                profile_picture=profile_picture,
            )

            # Send activation email when password is not set
            if not password:
                send_set_password_email(user)

        return user