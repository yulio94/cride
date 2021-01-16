"""Circle membership permissions classes"""

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership


class IsActiveCircleMember(BasePermission):
    """
    Allow access only to circle members.

    Expected that views implementing this permission has a `circle` attribute assigned.
    """

    def has_permission(self, request, view):
        """
        Verify user is an active member of the circle.
        """
        circle = view.circle
        try:
            Membership.objects.get(
                user=request.user,
                circle=circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True
