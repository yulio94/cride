"""User serializers"""

# Django rest framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

# Models
from cride.users.models import User, Profile

# Utilities
from datetime import timedelta
import jwt


class AccountVerificationSerializer(serializers.Serializer):
    """
    User account verification serializer.

    Handle token data validation.
    """

    token = serializers.CharField()

    def validate_token(self, data):
        """
        Verify token is valid.

        :param data:
        :return:
        """
        try:
            payload = jwt.decode(
                data,
                settings.SECRET_KEY,
                algorithms=['HS256'],
            )

        except jwt.ExpiredSignatureError as e:
            raise serializers.ValidationError(
                'Verification link has expired.'
            )

        except jwt.PyJWTError as e:
            raise serializers.ValidationError(
                'Invalid token'
            )

        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError(
                'Invalid token'
            )

        self.context['payload'] = payload

        return data

    def save(self, **kwargs):
        """
        Update users verify status

        :param kwargs:
        :return:
        """
        payload = self.context['payload']
        username = payload['user']

        user = User.objects.get(username)
        user.is_verified = True
        user.save()


class UserSignupSerializer(serializers.Serializer):
    """
    User sign up serializer.

    Handle sign up data validation and user/profile creation.
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        min_length=4,
        max_length=20,
    )
    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
    )
    phone_number = serializers.CharField(
        validators=[phone_regex]
    )
    # Password
    password = serializers.CharField(
        min_length=8,
        max_length=64,
        required=True,
    )
    password_confirmation = serializers.CharField(
        min_length=8,
        max_length=64,
        required=True,
    )
    # Name
    first_name = serializers.CharField(
        min_length=2,
        max_length=30,
    )
    last_name = serializers.CharField(
        min_length=2,
        max_length=30,
    )

    def validate(self, attrs):
        """Verify passwords match."""
        password = attrs['password']
        password_confirmation = attrs['password_confirmation']

        if password != password_confirmation:
            raise serializers.ValidationError(
                'Password doesn\'t match'
            )
        password_validation.validate_password(password)
        return attrs

    def create(self, validated_data):
        """
        Handle user and profile creation.

        :param validated_data:
        :return:
        """
        validated_data.pop('password_confirmation')
        user = User.objects.create_user(
            **validated_data,
            is_verified=False,
        )
        self.send_confirmation_email(user)
        Profile.objects.create(
            user=user
        )
        return user

    def send_confirmation_email(self, user):
        """
        Send account verification link to given user.
        """
        verification_token = self.gen_verification_token(user)
        subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
        from_email = 'Comparte Ride <noreply@comparteride.com>'
        content = render_to_string(
            'emails/users/account_verification.html',
            {'token': verification_token, 'user': user}
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(
            content,
            'text/html'
        )
        msg.send()

    @staticmethod
    def gen_verification_token(user):
        """
        Create JWT token that user can use to verify it's account.

        :param user:
        :return:
        """
        exp_date = timezone.now() + timedelta(days=3)
        payload = {
            'user': user.username,
            'exp': int(exp_date.timestamp()),
            'type': 'email_confirmation',
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256',
        )

        return token.decode()


class UserModelSerializer(serializers.ModelSerializer):
    """
    User model serializer
    """

    class Meta:
        """Meta class."""
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )


class UserLoginSerializer(serializers.Serializer):
    """
    User login serializer.

    Handle the login request data.
    """
    email = serializers.EmailField(
        required=True
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
    )

    def validate(self, attrs):
        """
        Check credentials
        """

        user = authenticate(
            username=attrs['email'],
            password=attrs['password']
        )

        if not user:
            raise serializers.ValidationError(
                'Invalid credentials'
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                'Account is not active yet'
            )

        self.context['user'] = user

        return attrs

    def create(self, validated_data):
        """Generate or retrieve a token."""

        token, created = Token.objects.get_or_create(
            user=self.context['user']
        )
        return self.context['user'], token.key
