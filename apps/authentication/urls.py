from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    VerifyEmailView,
)

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
    "login/",
    LoginView.as_view(),
    name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
    "logout/",
    LogoutView.as_view(),
    name="logout",
    ),
    path(
    "verify-email/",
    VerifyEmailView.as_view(),
    name="verify-email",
),
path("me/", MeView.as_view()),
 path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),

    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset",
    ),

    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
