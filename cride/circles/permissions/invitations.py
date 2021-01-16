"""Invitation model permissions"""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsSelfMember(BasePermission):
    """
    Check if the user that required an invitation list is the
    owner of the list.
    """

    def has_permission(self, request, view):
        """
        Let object only to member owners.
        """

        obj = view.get_object()
        return obj.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """
        Allow access only if member is owned by the requesting user.
        """
        return request.user == obj.user
