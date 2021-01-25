"""Invitation tests."""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework.test import APITestCase

# Models
from cride.circles.models import Invitation, Circle, Membership
from cride.users.models import User
from rest_framework.authtoken.models import Token


class InvitationManagerTestCase(TestCase):
    """Invitations manager test case."""

    def setUp(self) -> None:
        """Test case setup."""
        self.user = User.objects.create(
            first_name='Julio',
            last_name='Estrada',
            email='jestrada@mail.com',
            username='jestrada',
            password='admin123'
        )

        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='fciencias',
            about='Grupo oficial de la facultad de ciencias de la UNAM',
            verified=True
        )

    def test_code_generation(self):
        """Random codes should be generated automatically."""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one."""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique, a new one must be generated."""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        ).code

        # Create another invitation with the last code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        ).code

        self.assertNotEqual(code, invitation)


class MemberInvitationsAPITestCase(APITestCase):
    """"""

    def setUp(self) -> None:
        """Test case setup"""
        self.user = User.objects.create(
            first_name='Julio',
            last_name='Estrada',
            email='jestrada@mail.com',
            username='jestrada',
            password='admin123'
        )

        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='fciencias',
            about='Grupo oficial de la facultad de ciencias de la UNAM',
            verified=True
        )

        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.user.profile,
            circle=self.circle,
            remaining_invitations=10
        )

        self.token = Token.objects.create(user=self.user).key

    def test_response_success(self):
        """Verify request succeed."""
        # url = reverse()
