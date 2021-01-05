"""Circle views"""

# Django REST framework
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

# Models
from cride.circles.models import Circle

# Use case
from cride.circles.usecases.create_circle import CreateCircleUseCase

# Serializers
from cride.circles.serializers import CircleModelSerializer


class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Circle view set
    """
    serializer_class = CircleModelSerializer
    permission_classes = (IsAuthenticated,)

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
