# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'account/login/?$', views.login),
    url(r'account/register/?$', views.register),
    url(r'account/logout/?$', views.logout),
    url(r'account/settings/?$', views.account_settings),

    url(r'account/settings/mysign$', views.set_mysign),
)
