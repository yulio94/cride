"""Ride serializers"""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Ride
from cride.circles.models import Membership
from cride.users.models import User

# Serializers
from cride.users.serializers import UserModelSerializer

# Utilities
from datetime import timedelta
from django.utils import timezone


class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ('offered_by',
                            'offered_in',
                            'rating')

    def update(self, instance, validated_data):
        """Prevent an update when ride is stared"""
        now = timezone.now()
        if instance.departure_date <= now:
            raise serializers.ValidationError('Ongoing rides cannot be modified.')
        return super().update(instance, validated_data)


class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride serializer."""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """class Meta"""

        model = Ride
        exclude = ('offered_in',
                   'passengers',
                   'rating',
                   'is_active')

    @staticmethod
    def validate_departure_date(attr):
        """Verify date is not in the past."""
        min_date = timezone.now() + timedelta(minutes=10)
        if attr < min_date:
            raise serializers.ValidationError('Departure time must be at least pass the next 20 minutes windows.')
        return attr

    def validate(self, attrs):
        """
        Validate:

        Verify that person who offers the ride is a member and also the same user making the request.
        """
        circle = self.context['circle']
        user = attrs['offered_by']

        if self.context['request'].user != user:
            serializers.ValidationError('Rides offered on behalf of others are not allowed.')

        try:
            membership = Membership.objects.get(user=user,
                                                circle=circle,
                                                is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle.')

        if attrs['arrival_date'] <= attrs['departure_date']:
            raise serializers.ValidationError('Departure date must happen after of arrival date.')

        self.context['membership'] = membership

        return attrs

    def create(self, validated_data):
        """Create ride and update stats."""
        circle = self.context['circle']
        ride = Ride.objects.create(**validated_data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = validated_data['offered_by'].profile
        profile.rides_offered += 1
        profile.save()

        return ride


class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer."""

    passenger = serializers.IntegerField()

    class Meta:
        """Meta class."""
        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, attr):
        """Verify passenger exits and is a circle member."""
        try:
            user = User.objects.get(pk=attr)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid passenger.')

        circle = self.context['circle']
        if not Membership.objects.filter(user=user,
                                         circle=circle,
                                         is_active=True).exists:
            raise serializers.ValidationError('User is not an active member of the circle.')

        try:
            membership = Membership.objects.get(user=user,
                                                circle=circle,
                                                is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle.')

        self.context['user'] = user
        self.context['member'] = membership

        return attr

    def validate(self, attrs):
        """Verify rides allow new passengers."""
        ride = self.context['ride']

        if ride.departure_date <= timezone.now():
            raise serializers.ValidationError('You can\'t join this ride now')

        if ride.available_seats < 1:
            raise serializers.ValidationError('Ride is already full')

        if Ride.objects.filter(passengers__pk=attrs['passenger']):
            raise serializers.ValidationError('Passenger is already in this trip.')

    def update(self, instance, validated_data):
        """Add passenger to ride, and update stats"""
        ride = self.context['ride']
        circle = self.context['circle']
        user = self.context['user']

        ride.passengers.add(user)

        # Instance
        ride.avaialbe_seats -= 1
        ride.save()

        # Profile
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # Membership
        member = self.context['member']
        member.rides_taken += 1
        member.save()

        # Circle
        circle.rides_taken += 1
        circle.save()

        return ride


class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer."""
    current_time = serializers.DateTimeField()

    class Meta:
        model = Ride
        fields = ('is_active', 'current_time')

    def validate_current_time(self, attr):
        """Verify ride have indeed started."""
        ride = self.context['view'].get_object()
        if attr <= ride.departure_date:
            raise serializers.ValidationError('Ride has not started yet')
        return attr
