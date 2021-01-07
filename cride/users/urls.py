"""Users urls"""

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Django
from django.urls import path, include

# Views
from cride.users import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
