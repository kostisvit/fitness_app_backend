from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
    "user",
    "first_name",
    "last_name",
    "date_of_birth",
    "gender",
    "height",
    "weight",
    "experience_level",
    "fitness_goal",
    "created",
    "modified",
    )
    search_fields = ("user__email", "first_name", "last_name")
    date_hierarchy = "created"
    list_filter = ("gender", "experience_level", "fitness_goal", "units")
