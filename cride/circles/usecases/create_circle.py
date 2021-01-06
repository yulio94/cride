"""Business logic and uses cases of circles"""

# Utils
from cride.utils.usecases import BaseUseCase

# Models
from cride.circles.models.meberships import Membership


class CreateCircleUseCase(BaseUseCase):
    """
    Create both circle and membership.
    Assign the user that create the circle as an admin of the membership.
    """

    def __init__(self, serializer, request):
        """

        :param serializer:
        """
        self.serializer = serializer
        self.request = request

    def use_case(self):
        """"""
        circle = self.serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )
