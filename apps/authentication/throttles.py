
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "auth_login"


class RegisterRateThrottle(AnonRateThrottle):
    scope = "auth_register"


class ResendVerificationRateThrottle(AnonRateThrottle):
    scope = "auth_resend_verification"


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = "auth_password_reset"


class PasswordResetConfirmRateThrottle(AnonRateThrottle):
    scope = "auth_password_reset_confirm"
