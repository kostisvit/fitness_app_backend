
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.IsAuthenticated",
        ),
        "DEFAULT_THROTTLE_RATES": {
            "auth_login": "1000/minute",
            "auth_register": "1000/hour",
            "auth_resend_verification": "1000/hour",
            "auth_password_reset": "1000/hour",
            "auth_password_reset_confirm": "1000/hour",
        },
    }
)

class AuthenticationTests(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.email = "john@example.com"
        self.password = "TestPassword123!"

        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")

        self.verify_url = reverse("verify-email")
        self.resend_verification_url = reverse(
            "resend-verification"
        )

        self.password_reset_url = reverse(
            "password-reset"
        )
        self.password_reset_confirm_url = reverse(
            "password-reset-confirm"
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def create_user(
        self,
        email=None,
        password=None,
        verified=True,
    ):
        user = User.objects.create_user(
            email=email or self.email,
            password=password or self.password,
            role=User.Role.MOBILE,
            is_active=True,
            email_verified=verified,
        )

        return user

    def login_user(self, user=None):
        user = user or self.create_user()

        response = self.client.post(
            self.login_url,
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def test_register_success(self):
        response = self.client.post(
            self.register_url,
            {
                "email": self.email,
                "password": self.password,
                "password_confirm": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            email=self.email
        )

        self.assertFalse(user.email_verified)
        self.assertTrue(user.is_active)
        self.assertEqual(
            user.role,
            User.Role.MOBILE,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_register_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            {
                "email": self.email,
                "password": self.password,
                "password_confirm": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(
                email=self.email
            ).exists()
        )

    def test_register_duplicate_email(self):
        self.create_user()

        response = self.client.post(
            self.register_url,
            {
                "email": self.email,
                "password": self.password,
                "password_confirm": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # Email verification
    # ---------------------------------------------------------

    def test_verify_email_success(self):
        user = self.create_user(
            verified=False
        )

        response = self.client.post(
            self.resend_verification_url,
            {
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email_body = mail.outbox[0].body

        token = email_body.split(
            "Verification token:\n"
        )[1].split("\n")[0]

        response = self.client.post(
            self.verify_url,
            {
                "token": token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        user.refresh_from_db()

        self.assertTrue(
            user.email_verified
        )

    def test_verify_invalid_token(self):
        response = self.client.post(
            self.verify_url,
            {
                "token": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------

    def test_login_success(self):
        user = self.create_user()

        response = self.client.post(
            self.login_url,
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

        self.assertEqual(
            response.data["user"]["email"],
            user.email,
        )

    def test_login_wrong_password(self):
        user = self.create_user()

        response = self.client.post(
            self.login_url,
            {
                "email": user.email,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_unverified_user(self):
        user = self.create_user(
            verified=False
        )

        response = self.client.post(
            self.login_url,
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_inactive_user(self):
        user = self.create_user()
        user.is_active = False
        user.save(
            update_fields=["is_active"]
        )

        response = self.client.post(
            self.login_url,
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # /me/
    # ---------------------------------------------------------

    def test_me_requires_authentication(self):
        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_success(self):
        data = self.login_user()

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {data['access']}"
            )
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            self.email,
        )

        self.assertTrue(
            response.data["email_verified"]
        )

    # ---------------------------------------------------------
    # Refresh token
    # ---------------------------------------------------------

    def test_refresh_token(self):
        data = self.login_user()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": data["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    # ---------------------------------------------------------
    # Logout
    # ---------------------------------------------------------

    def test_logout_blacklists_refresh_token(self):
        data = self.login_user()

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {data['access']}"
            )
        )

        response = self.client.post(
            self.logout_url,
            {
                "refresh": data["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_205_RESET_CONTENT,
        )

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": data["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ---------------------------------------------------------
    # Password reset
    # ---------------------------------------------------------

    def test_password_reset_request(self):
        user = self.create_user()

        response = self.client.post(
            self.password_reset_url,
            {
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_password_reset_unknown_email(self):
        response = self.client.post(
            self.password_reset_url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_password_reset_confirm(self):
        user = self.create_user()

        self.client.post(
            self.password_reset_url,
            {
                "email": user.email,
            },
            format="json",
        )

        email_body = mail.outbox[0].body

        reset_url = email_body.split(
            "http://localhost:3000/reset-password?token="
        )[1].split("\n")[0]

        new_password = "NewPassword123!"

        response = self.client.post(
            self.password_reset_confirm_url,
            {
                "token": reset_url,
                "password": new_password,
                "password_confirm": new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        user.refresh_from_db()

        self.assertTrue(
            user.check_password(
                new_password
            )
        )

    def test_password_reset_password_mismatch(self):
        user = self.create_user()

        response = self.client.post(
            self.password_reset_url,
            {
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            self.password_reset_confirm_url,
            {
                "token": "anything",
                "password": "NewPassword123!",
                "password_confirm": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # Resend verification
    # ---------------------------------------------------------

    def test_resend_verification(self):
        user = self.create_user(
            verified=False
        )

        response = self.client.post(
            self.resend_verification_url,
            {
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_resend_verification_unknown_email(self):
        response = self.client.post(
            self.resend_verification_url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )
