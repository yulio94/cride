"""Ride views"""

# Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# Serializers
from cride.rides.serializers import (CreateRideSerializer, RideModelSerializer, JoinRideSerializer)

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter

# Models
from cride.circles.models import Circle

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsActiveCircleMember
from cride.rides.permissions import IsRideOwner, IsNotRideOwner

# Utilities
from django.utils import timezone
from datetime import timedelta


class RideViewSet(mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """Ride view set."""

    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('departure_date', 'arrival_date', 'available_seats')
    ordering_fields = ('departure_date', 'arrival_date', 'available_seats')
    search_fields = ('departure_location', 'arrival_location')
    circle = None

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that circle exists.
        """
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(
            Circle,
            slug_name=slug_name
        )
        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsRideOwner)
        if self.action in ['join']:
            permissions.append(IsNotRideOwner)
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'update':
            return JoinRideSerializer
        return RideModelSerializer

    def get_serializer_context(self):
        """Add circle to serializer context"""
        context = super().get_serializer_context()
        context['circle'] = self.circle
        return context

    def get_queryset(self):
        """Return active circle rides"""
        offset = timezone.now() + timedelta(minutes=10)
        return self.circle.ride_set.filter(departure_date__gte=offset,
                                           available_seats_gte=1)

    @action(detail=True, methods=['POST'])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride."""
        ride = self.get_object()
        serializer = self.get_serializer_class()
        serializer(ride,
                   data={'passenger': request.user.pk},
                   context={'ride': ride, 'circle': self.circle},
                   partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)
