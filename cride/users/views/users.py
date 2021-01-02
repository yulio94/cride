"""users views"""

# Django rest framework
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Serializers
from cride.users.serializers import (UserLoginSerializer, UserModelSerializer, UserSignupSerializer,
                                     AccountVerificationSerializer)


class UserLoginAPIView(APIView):
    """User login API view"""

    @staticmethod
    def post(request, *args, **kwargs):
        """Handle http post request"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        # Serialize response
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)


class UserSignupAPIView(APIView):
    """User sign up API view"""

    @staticmethod
    def post(request, *args, **kwargs):
        """Handle http post request"""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


class AccountVerificationAPIView(APIView):
    """Account verification API view"""

    @staticmethod
    def post(request, *args, **kwargs):
        """Handle http post request"""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Congrats, now go share some rides!'}
        return Response(data, status=status.HTTP_200_OK)
