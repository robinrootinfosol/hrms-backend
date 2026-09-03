from django.urls import path
from authentication.views import LoginView, set_password_view, ForgetPasswordView,reset_password_view,RequestPasswordResetAPIView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('forgot-password/', ForgetPasswordView.as_view(), name='auth-forgot-password'),
    path('set-password/<str:uidb64>/<str:token>/', set_password_view, name='set-password-web'),
    path('reset-password/', RequestPasswordResetAPIView.as_view(), name='auth-reset-password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password_view, name='reset-password-web'),
]