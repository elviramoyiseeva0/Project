from django.conf import settings
from django.db import models

from NeiroSlopTerest.models import Pin


class Board(models.Model):
    """Collection of pins owned by a registered user or a guest session."""

    GUEST_BOARD_LIMIT = 2

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="boards",
    )
    session_key = models.CharField(max_length=40, blank=True, default="", db_index=True)
    pins = models.ManyToManyField(Pin, blank=True, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
