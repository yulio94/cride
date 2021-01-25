"""User serializers"""

# Django rest framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.conf import settings

# Models
from cride.users.models import User, Profile

# Serializers
from cride.users.serializers.profiles import ProfileModelSerializer

# Tasks
from cride.taskapp.tasks import send_confirmation_email

# Utilities
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

        user = User.objects.get(username=username)
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
        user = User.objects.create_user(**validated_data,
                                        is_verified=False,
                                        is_client=True,
                                        )
        send_confirmation_email.delay(user.pk)
        Profile.objects.create(
            user=user
        )
        return user


class UserModelSerializer(serializers.ModelSerializer):
    """
    User model serializer
    """

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        """Meta class."""
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile'
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
