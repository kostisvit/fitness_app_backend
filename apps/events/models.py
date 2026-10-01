import uuid

from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel


class Sport(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SportEvent(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )

    sport = models.ForeignKey(
        Sport,
        on_delete=models.PROTECT,
        related_name="events",
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    date = models.DateField()
    time = models.TimeField()

    place = models.CharField(max_length=255)

    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title
