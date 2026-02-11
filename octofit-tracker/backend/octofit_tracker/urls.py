"""octofit_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.response import Response
import os

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'activities', views.ActivityViewSet, basename='activity')
router.register(r'workouts', views.WorkoutViewSet, basename='workout')
router.register(r'leaderboard', views.LeaderboardViewSet, basename='leaderboard')

# Build API root using Codespaces URL when available to avoid certificate issues
CODESPACE_NAME = os.environ.get('CODESPACE_NAME')
if CODESPACE_NAME:
    # Use http scheme for Codespaces preview domain to avoid certificate issues in local testing
    API_BASE = f"http://{CODESPACE_NAME}-8000.app.github.dev"
else:
    API_BASE = None


def api_root_env(request, format=None):
    if API_BASE:
        return Response({
            'users': f"{API_BASE}/api/users/",
            'teams': f"{API_BASE}/api/teams/",
            'activities': f"{API_BASE}/api/activities/",
            'workouts': f"{API_BASE}/api/workouts/",
            'leaderboard': f"{API_BASE}/api/leaderboard/",
        })
    # fallback to default view which uses request host
    return views.api_root(request, format=format)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', api_root_env, name='api-root'),
]
