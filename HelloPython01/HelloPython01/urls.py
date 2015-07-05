"""HelloPython01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from HelloPython01 import views
from HelloPython02.views import HelloWorld
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^hello02tmp$', TemplateView.as_view(template_name='HelloPython02/index.html')),
    url(r'^hello02$', HelloWorld.as_view()),
    url(r'^$', views.home),
    url(r'^plus$', views.plus),
    url(r'^login$', views.login),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^.+$', views.home),
]

