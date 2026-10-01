from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "role",
        "email_verified",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )
    search_fields = ("email",)

    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),
        ("Permissions", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "email_verified",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "role",
                "is_active",
                "is_staff",
            ),
        }),
    )
