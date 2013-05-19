# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'notifies$', views.get_notifies),
    url(r'notify/confirm$', views.confirm_notify),
)
