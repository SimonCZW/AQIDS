# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'mainapp'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^test/$', views.TestIndexView.as_view(), name='indextest'),
]
