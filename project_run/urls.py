"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import company_details, RunViewSet, UserViewSet, StartRunView, StopRunView, start_run_view, \
    stop_run_view, AthleteInfoView, Athlete_infoViewSet, ChallengeViewSet, PositionViewSet, CollectibleItemViewSet, \
    UploadFileView, SubscribeToCoachView

router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)
router.register('api/athlete_info', Athlete_infoViewSet),
router.register('api/challenges', ChallengeViewSet)
router.register('api/positions', PositionViewSet)
router.register('api/collectible_item', CollectibleItemViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('', include(router.urls)),
    path('api/runs/<int:run_id>/start/', StartRunView.as_view(), name='start_run'),
    path('api/runs/<int:run_id>/stop/', StopRunView.as_view(), name='stop_run'),
    path('api/athlete_info/<int:user_id>/', AthleteInfoView.as_view(), name='athlete_info'),
    path('api/upload_file/', UploadFileView.as_view()),
    path('api/subscribe_to_coach/<int:id>/', SubscribeToCoachView.as_view(), name='subscribe_to_coach'),


    #method_2: @api_view
#     path('api/runs/<int:run_id>/start/', start_run_view),
#     path('api/runs/<int:run_id>/stop/', stop_run_view),
 ] + debug_toolbar_urls()