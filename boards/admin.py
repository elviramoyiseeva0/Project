from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "session_key", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description", "owner__username", "session_key")
    filter_horizontal = ("pins",)
