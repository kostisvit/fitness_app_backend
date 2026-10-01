from django.conf import settings
from django.core.mail import send_mail

from .tokens import create_email_verification_token, create_password_reset_token


def send_verification_email(user):
    token = create_email_verification_token(user)

    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email"
        f"?token={token}"
    )

    send_mail(
        subject="Verify your email",
        message=(
            "Hello,\n\n"
            "Please verify your email address by opening this link:\n\n"
            f"{verification_url}\n\n"
            "Verification token:\n"
            f"{token}\n\n"
            "This link expires in 24 hours.\n\n"
            "If you did not create an account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_password_reset_email(user):
    token = create_password_reset_token(user)

    reset_url = (
        f"{settings.FRONTEND_URL}/reset-password"
        f"?token={token}"
    )

    send_mail(
        subject="Reset your password",
        message=(
            "Hello,\n\n"
            "We received a request to reset your password.\n\n"
            f"Reset URL:\n{reset_url}\n\n"
            f"RESET TOKEN:\n{token}\n\n"
            "This link expires in 1 hour.\n\n"
            "If you did not request a password reset, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
