from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import account_activation_token
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated. Please contact HR.")

        if not user.has_usable_password() or user.is_first_login:
            raise serializers.ValidationError(
                "You have not set your account password yet. Please check your email to set your password before logging in."
            )

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        # Create or retrieve the 40-character token
        token, _ = Token.objects.get_or_create(user=user)

        return {
            'success':True,
            'token': token.key,
            'user': {
                'id': str(user.id),
                'employee_id': user.employee_id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_first_login': user.is_first_login,
                'biometric_enabled': user.biometric_enable,
            }
        }

class SetPasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True,min_length=8,required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password do not match"})
        return attrs

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self,value):
        return value.lower().strip()
    
class ResetPasswordConfirmAPISerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid or expired token link."})

        if not account_activation_token.check_token(user, attrs['token']):
            raise serializers.ValidationError({"token": "Invalid or expired reset token."})

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.is_first_login = False
        user.save()
        return user

class PasswordResetResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()