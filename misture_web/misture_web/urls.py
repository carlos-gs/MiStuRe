# coding=utf-8
"""misture_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import django.contrib.auth.views
from examen import views as examen_views


urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^examen/', include('examen.urls')),
    url(r'^accounts/login/{0,1}$', django.contrib.auth.views.LoginView.as_view(
        template_name='login.html'), name='login'),
    url(r'^accounts/logout$', django.contrib.auth.views.logout,
        {'next_page': 'login'}, name='logout'),
    url(r'.*', examen_views.redirect_to_index)  # /views.noencontrado*/)
    
]
