from django.core import signing

VERIFICATION_SALT = "email-verification"
PASSWORD_RESET_SALT = "password-reset"

def create_email_verification_token(user):
    return signing.dumps(
        {
            "user_id": str(user.id),
            "email": user.email,
        },
        salt=VERIFICATION_SALT,
    )


def verify_email_verification_token(token, max_age=60 * 60 * 24):
    """
    Token is valid for 24 hours.
    """

    return signing.loads(
        token,
        salt=VERIFICATION_SALT,
        max_age=max_age,
    )


def create_password_reset_token(user):
    return signing.dumps(
        {
            "user_id": str(user.id),
            "email": user.email,
            "password_hash": user.password,
        },
        salt=PASSWORD_RESET_SALT,
    )


def verify_password_reset_token(token, max_age=60 * 60):
    return signing.loads(
        token,
        salt=PASSWORD_RESET_SALT,
        max_age=max_age,
    )
