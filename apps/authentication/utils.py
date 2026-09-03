from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}{user.is_active}"

account_activation_token = AccountActivationTokenGenerator()

def send_set_password_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    setup_url = f"{settings.FRONTEND_OR_WEB_URL}/api/v1/auth/set-password/{uidb64}/{token}/"
    subject = "Welcome to the Team! Set you HRMS account password."
    message = f"""Hi {user.full_name},

            Welcome to the company! Your HRMS employee account has been created.
            Your Employee ID is: {user.employee_id}

            Please click the link below to set your account password and activate your access:
            {setup_url}

            This link is valid for 24 hours.

            Best regards,  
            HR Operations Team
            """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def send_forget_password_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    reset_url = f"{settings.FRONTEND_OR_WEB_URL}/api/v1/auth/reset-password/{uidb64}/{token}/"

    subject = "Reset Your HRMS Account Password"
    message = f"""Hi {user.full_name},

        We received a request to reset the password for your HRMS account ({user.employee_id}).

        Click the link below to set a new password:
        {reset_url}

        If you did not request this, you can safely ignore this email. Your password will remain unchanged.
        This link will expire in 24 hours.

        Best regards,  
        HR Operations Team
        """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def send_reset_password_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    reset_url = f"{settings.FRONTEND_OR_WEB_URL}/api/v1/auth/reset-password/{uidb64}/{token}/"

    subject = "Reset Your HRMS Password"
    message = f"""Hi {user.full_name},

        A password reset was requested for your HRMS account ({user.employee_id}).

        Click the link below to set a new password:
        {reset_url}

        This link is valid for 24 hours. If you did not initiate this request, please contact IT immediately.

        Best regards,  
        HR Operations Team
        """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
