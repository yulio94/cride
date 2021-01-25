"""Ride urls"""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from cride.rides.views import RideViewSet

router = DefaultRouter()
router.register(
    r'circles/(?P<slug_name>[-a-zA-Z0-9_-]+)/rides',
    RideViewSet,
    basename='ride'
)

urlpatterns = [
    path('', include(router.urls))
]
