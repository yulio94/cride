"""Circle views"""

# Django REST framework
from rest_framework import viewsets, mixins

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleAdmin

# Models
from cride.circles.models import Circle

# Use case
from cride.circles.usecases.create_circle import CreateCircleUseCase

# Serializers
from cride.circles.serializers import CircleModelSerializer

 # Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Circle view set
    """
    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ('verified', 'is_limited')

    # Search fields
    search_fields = ('slug_name', 'name')

    # ordering
    ordering_fields = ('rides_offered', 'rides_taken', 'name', 'created', 'member_limit')
    ordering = ('-members__count', '-rides_offered', '-rides_taken')

    def get_queryset(self):
        """
        Restrict list to public-only.
        :return:
        """
        queryset = Circle.objects.all()

        if self.action == 'list':
            queryset = Circle.objects.filter(is_public=True)

        return queryset

    def perform_create(self, serializer):
        """
        Execute use case

        :param serializer:
        :return:
        """
        self.execute_use_case(serializer)

    def execute_use_case(self, serializer):
        """"""
        use_case = CreateCircleUseCase(
            serializer,
            self.request
        )
        use_case.execute()

    def get_permissions(self):
        """
        Assign permissions based on action.

        :return:
        """
        permissions = [IsAuthenticated]

        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)

        return [permission() for permission in permissions]
