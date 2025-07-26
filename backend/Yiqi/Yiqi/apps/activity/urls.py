"""Yiqi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from activity.views import ActivityTypeView, UploadTextDateView, SlideIndexViewSet, SearchAllDateViewSet, \
    MapModelAllDateViewSet, StartAllDataViewSet, RegistrationAllDataViewSet

app_name = 'activity'

router = DefaultRouter()

router.register(r'ActivityTypeView', ActivityTypeView, basename='ActivityTypeView')  # 登陆
router.register(r'SlideIndexViewSet', SlideIndexViewSet, basename='SlideIndexViewSet')
router.register(r'SearchAllDateViewSet', SearchAllDateViewSet, basename='SearchAllDateViewSet')
router.register(r'MapModelAllDateViewSet', MapModelAllDateViewSet, basename='MapModelAllDateViewSet')
router.register(r'StartAllDataViewSet', StartAllDataViewSet, basename='StartAllDataViewSet')
router.register(r'RegistrationAllDataViewSet', RegistrationAllDataViewSet, basename='RegistrationAllDataViewSet')

urlpatterns = [
    path('', include(router.urls)),
    path('UploadTextDateView/', UploadTextDateView.as_view(), name='UploadTextDateView'),  # 保存活动数据
]
