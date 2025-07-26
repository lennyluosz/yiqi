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

from users.views import Registered, ObtainJSONWebToken, GetUser

app_name = 'users'

router = DefaultRouter()
router.register(r'Registered', Registered, basename='Registered')  # 注册

urlpatterns = [
    path('', include(router.urls)),
    path('login/', ObtainJSONWebToken.as_view()),  # 登录
    path('GetUser/', GetUser.as_view(), name='GetUser'),  # 用户
]
