"""Circles admin registry"""

# Django
from django.contrib import admin

# Models
from .models.circles import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """
    Circle admin
    """

    list_display = (
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit',
    )

    search_fields = (
        'slug_name',
        'name'
    )

    list_filter = (
        'is_public',
        'verified',
        'is_limited',
    )
