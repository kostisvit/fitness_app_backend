from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .tokens import verify_email_verification_token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
        )

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=User.Role.MOBILE,
            is_active=True,
            email_verified=False,
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs["email"].lower().strip()
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        if not user.email_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        }


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            data = verify_email_verification_token(value)
        except signing.SignatureExpired:
            raise serializers.ValidationError(
                "Verification link has expired."
            )
        except signing.BadSignature:
            raise serializers.ValidationError(
                "Invalid verification link."
            )

        try:
            user = User.objects.get(
                id=data["user_id"],
                email=data["email"],
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid verification link."
            )

        if user.email_verified:
            raise serializers.ValidationError(
                "Email is already verified."
            )

        self.user = user
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })

        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()
