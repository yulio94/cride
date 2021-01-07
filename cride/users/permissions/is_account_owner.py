"""User permissions"""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsAccountOwner(BasePermission):
    """
    Allow access only to objects owned by the requesting user
    """

    message = 'You aren\'t allowed to view details about this user'

    def has_object_permission(self, request, view, obj):
        """
        Check obj and user are the same

        :param request:
        :param view:
        :param obj:
        :return:
        """
        print(request.user, obj)
        return request.user == obj
