"""Circles urls"""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from cride.circles.views import CircleViewSet

router = DefaultRouter()
router.register(r'circles', CircleViewSet, basename='circle')

urlpatterns = [
    path('', include(router.urls))
]
