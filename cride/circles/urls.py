"""Circles urls"""

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from cride.circles.views import CircleViewSet, MembershipViewSet

router = DefaultRouter()
router.register(r'circles', CircleViewSet, basename='circle')
router.register(
    r'circles/(?P<slug_name>[-a-zA-Z0-9_-]+)/members',
    MembershipViewSet,
    basename='membership'
)

urlpatterns = [
    path('', include(router.urls))
]
