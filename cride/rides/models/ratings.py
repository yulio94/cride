"""Rating model"""

# Django
from django.db import models

# Utilities
from cride.utils.models import CRideModel


class Rating(CRideModel):
    """Model to manage user qualifications of a ride"""
    rating_user = models.ForeignKey('users.User',
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    help_text='User that emits the rating',
                                    related_name='rating_user')
    rated_user = models.ForeignKey('users.User',
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   help_text='User that receives the rating.',
                                   related_name='rated_user')
    circle = models.ForeignKey('circles.Circle',
                               on_delete=models.CASCADE)
    ride = models.ForeignKey('rides.Ride',
                             on_delete=models.CASCADE,
                             related_name='rated_ride')
    comments = models.TextField(max_length=1000,
                                blank=True)
    rating = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        """String model representation"""
        return '@{} rated {} @{}'.format(self.rating_user.username,
                                         self.rating,
                                         self.rated_user.username)
