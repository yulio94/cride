"""Rating class serializers"""

# Django
from django.db.models import Avg

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Rating


class CreateRideRatingSerializer(serializers.ModelSerializer):
    """ Create ride rating serializer."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    comments = serializers.CharField(required=False)

    class Meta:
        """Meta class."""
        model = Rating
        fields = ('rating', 'comments')

    def validate(self, attrs):
        """Verify that rating hasn't been before."""
        user = self.context['request'].user
        ride = self.context['ride']

        if not ride.passengers.filter(pk=user.pk).exists():
            raise serializers.ValidationError('Current user isn\'t a passenger')

        query = Rating.objects.filter(rating_by=user,
                                      ride=ride,
                                      circle=self.context['circle'])

        if query.exists():
            raise serializers.ValidationError('Rating already issued.')

    def create(self, validated_data):
        """Create rating."""
        offered_by = self.context['ride'].offered_by

        Rating.objects.create(
            circle=self.context['circle'],
            ride=self.context['ride'],
            rating_user=self.context['request'].user,
            rated_user=offered_by,
            **validated_data
        )

        ride_average = round(
            Rating.objects.create(circle=self.context['circle'],
                                  ride=self.context['ride']
                                  ).aggregate(Avg('rating'))['rating__avg'], 1)
        self.context['ride'].rating = ride_average
        self.context['ride'].save()

        user_avg = round(
            Rating.objects.filter(
                rated_user=offered_by
            ).aggregate(Avg('rating'))['rating__avg'],
            1
        )
        offered_by.profile.reputation = user_avg
        offered_by.profile.save()

        return self.context['ride']
