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
from django.contrib import admin
import xadmin  # 重新启用xadmin
from django.views.static import serve
from django.urls import path, include, re_path

from Yiqi.settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT

urlpatterns = [
    path('YiqiAdmin0001shujian/', include(xadmin.site.urls)),  # 重新启用xadmin
    path('admin/', admin.site.urls),  # 保留Django原生admin作为备用
    re_path(r'^upload/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
    path('users/', include('users.urls', namespace='users')),
    path('activity/', include('activity.urls', namespace='activity')),
    path('SharingSet/', include('SharingSet.urls', namespace='SharingSet')),
    path('userOperation/', include('userOperation.urls', namespace='userOperation')),
    path('messages/', include('messagess.urls', namespace='messages')),
]
