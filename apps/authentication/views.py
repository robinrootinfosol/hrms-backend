from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from authentication.serializers import LoginSerializer, SetPasswordConfirmSerializer, ForgetPasswordSerializer,ResetPasswordConfirmAPISerializer,PasswordResetResponseSerializer
from authentication.utils import account_activation_token, send_forget_password_email,send_reset_password_email

User = get_user_model()


class LoginView(generics.GenericAPIView):
    """
    User login endpoint returning JWT access/refresh tokens and profile metadata.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'data': serializer.validated_data
            },
            status=status.HTTP_200_OK
        )


def set_password_view(request, uidb64, token):
    """
    HTML Web Page View: Renders password setup form and activates the account upon submission.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not account_activation_token.check_token(user, token):
        return render(request, 'authentication/set_password.html', {'invalid_token': True})

    if request.method == 'POST':
        serializer = SetPasswordConfirmSerializer(data=request.POST)
        if serializer.is_valid():
            new_password = serializer.validated_data['password']
            user.set_password(new_password)
            user.is_first_login = False
            user.save()
            return render(request, 'authentication/set_password.html', {'success': True})
        else:
            return render(
                request,
                'authentication/set_password.html',
                {'user': user, 'errors': serializer.errors}
            )

    return render(request, 'authentication/set_password.html', {'user': user})


class ForgetPasswordView(generics.GenericAPIView):
    """
    Forgot Password API: Dispatches reset link if active account matches email.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(email=email, is_active=True).first()
        if user:
            send_forget_password_email(user)

        return Response(
            {
                'success':True,
                'message':'If an active account exists with this email, a password reset link has been sent.'
            },
            status=status.HTTP_200_OK
        )



class RequestPasswordResetAPIView(generics.GenericAPIView):
    """
    Authenticated Reset Password Request:
    Reads user identity from the 'Token <key>' header and emails a reset link.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetResponseSerializer

    @extend_schema(
        request=None,
        responses={200: PasswordResetResponseSerializer},
        summary="Trigger password reset link for the authenticated user"
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        send_reset_password_email(user)

        return Response(
            {
                'success': True,
                'message': f'Password reset link has been dispatched to {user.email}.'
            },
            status=status.HTTP_200_OK
        )


def reset_password_view(request, uidb64, token):
    """
    HTML Web Page View: Renders the password form and updates credentials upon submission.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not account_activation_token.check_token(user, token):
        return render(request, 'authentication/reset_password.html', {'invalid_token': True})

    if request.method == 'POST':
        serializer = SetPasswordConfirmSerializer(data=request.POST)
        if serializer.is_valid():
            new_password = serializer.validated_data['password']
            user.set_password(new_password)
            user.is_first_login = False
            user.save()
            return render(request, 'authentication/reset_password.html', {'success': True})
        else:
            return render(
                request,
                'authentication/reset_password.html',
                {'user': user, 'errors': serializer.errors}
            )

    return render(request, 'authentication/reset_password.html', {'user': user})

    