""""Django models utilities"""

# Django
from django.db import models


class CRideModel(models.Model):
    """Comparte ride base model

    CrideModel acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    every table with the following attributes:
        + created (DateTime): Save the datetime when the object was created
        + modified (DateTime): Save the datetime when the object was modified
    """
    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the object created.'
    )
    modified = models.DateTimeField(
        'created at',
        auto_now=True,
        help_text='Date time on which the object modified.'
    )

    class Meta:
        abstract = True

        get_latest_by = 'created'

        ordering = ['-created', '-modified']
