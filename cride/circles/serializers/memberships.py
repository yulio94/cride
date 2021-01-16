"""Circle membership serializers"""

# Django
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Membership, Invitation

# Serializers
from cride.users.serializers import UserModelSerializer


class MembershipModelSerializer(serializers.ModelSerializer):
    """
    Member model serializer
    """

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(source='created', read_only=True)

    class Meta:
        """
        Meta class
        """
        model = Membership
        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'rides_taken',
            'rides_offered',
            'joined_at',
            'invited_by'
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'invited_by',
        )


class AddMemberSerializer(serializers.Serializer):
    """
    Add member serializer.

    Handle addition of a new member to a circle.

    Circle object must be provided in the context.
    """

    invitation_code = serializers.CharField(min_length=10)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, attr):
        """
        Verify user isn't already a member
        """
        circle = self.context['circle']
        user = attr
        q = Membership.objects.filter(circle=circle, user=user)
        if q.exists():
            raise serializers.ValidationError('User already exists in this circle')
        return attr

    def validate_invitation_code(self, attr):
        """
        Verify code exists and that it's related to the circle.
        """

        try:
            invitation = Invitation.objects.get(code=attr,
                                                circle=self.context['circle'],
                                                used=False)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('Invalid invitation code')
        self.context['invitation'] = invitation
        return attr

    def validate(self, attrs):
        """
        Verify circle is capable of accepting new members.
        """
        circle = self.context['circle']
        if circle.is_limited and circle.members.count >= circle.members_limit:
            raise serializers.ValidationError('Circle has reached it\'s members limit')
        return attrs

    def create(self, validated_data):
        """
        Create new circle member and update circle info.
        """
        circle = self.context['circle']
        invitation = self.context['invitation']
        user = validated_data['user']

        now = timezone.now()

        # Member creation
        member = Membership.objects.create(user=user,
                                           profile=user.profile,
                                           circle=circle,
                                           invited_by=invitation.issued_by)

        # Update invitation
        invitation.used_by = user
        invitation.used = True
        invitation.used_at = now
        invitation.save()

        # Update issuer data
        issuer = Membership.objects.get(user=invitation.issued_by,
                                        circle=circle)
        issuer.used_inviations += 1
        issuer.remaining_invitations -= 1
        issuer.save()

        return member
