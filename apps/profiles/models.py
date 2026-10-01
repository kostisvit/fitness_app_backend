import uuid

from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"

    class FitnessGoal(models.TextChoices):
        LOSE_WEIGHT = "lose_weight", "Lose weight"
        BUILD_MUSCLE = "build_muscle", "Build muscle"
        GET_FIT = "get_fit", "Get fit"
        IMPROVE_ENDURANCE = "improve_endurance", "Improve endurance"

    class ExperienceLevel(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Units(models.TextChoices):
        METRIC = "metric", "Metric"
        IMPERIAL = "imperial", "Imperial"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=30,
        choices=Gender.choices,
        blank=True,
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fitness_goal = models.CharField(
        max_length=30,
        choices=FitnessGoal.choices,
        blank=True,
    )

    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        blank=True,
    )

    units = models.CharField(
        max_length=10,
        choices=Units.choices,
        default=Units.METRIC,
    )

    def __str__(self):
        return f"{self.user.email} profile"
