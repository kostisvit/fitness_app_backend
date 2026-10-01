from django.conf import settings
from django.core.mail import send_mail

from .tokens import create_email_verification_token


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
