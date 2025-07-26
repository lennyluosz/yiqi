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

from userOperation.views import SharingUserViewSet, BrowseUserViewSet, QrCodeApiViewset, ActivityUserInfoViewSet, \
    ClooectionViewSet, ReportionViewSet, RegisteredUserViewSet, CommentsModelsUserViewSet, UserAllActivityView, \
    UserbrowseView, CollectionUserView, ActivityUserinfoView, FeedBackViewSet

app_name = 'userOperation'

router = DefaultRouter()

router.register(r'UserAllActivityView', UserAllActivityView, basename='UserAllActivityView')
router.register(r'UserbrowseView', UserbrowseView, basename='UserbrowseView')
router.register(r'CollectionUserView', CollectionUserView, basename='CollectionUserView')
router.register(r'ActivityUserinfoView', ActivityUserinfoView, basename='ActivityUserinfoView')

urlpatterns = [
    path('', include(router.urls)),
    path('SharingUserViewSet/', SharingUserViewSet.as_view(), name='SharingUserViewSet'),  # 保存活动数据
    path('BrowseUserViewSet/', BrowseUserViewSet.as_view(), name='BrowseUserViewSet'),  # 保存浏览用户
    path('QrCodeApi/', QrCodeApiViewset.as_view(), name='QrCodeApiViewset'),
    path('ActivityUserInfo/', ActivityUserInfoViewSet.as_view(), name='ActivityUserInfo'),
    path('ClooectionViewSet/', ClooectionViewSet.as_view(), name='ClooectionViewSet'),
    path('ReportionViewSet/', ReportionViewSet.as_view(), name='ReportionViewSet'),
    path('RegisteredUserViewSet/', RegisteredUserViewSet.as_view(), name='RegisteredUserViewSet'),
    path('CommentsModelsUserViewSet/', CommentsModelsUserViewSet.as_view(), name='CommentsModelsUserViewSet'),
    path('FeedBackViewSet/', FeedBackViewSet.as_view(), name='FeedBackViewSet')
]
