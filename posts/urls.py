# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, kwargs={'p': 1}),
    url(r'p/(?P<p>\d+)/?$', views.index),
    url(r'posts/(?P<post_id>\d+)$', views.show_post, name='show_post'),
    url(r'posts/head/new$', views.post_new_head),
    url(r'posts/body/new$', views.post_new_body),
    # url(r'score/post/good/(?P<pid>\d+)$', views.post_scoring.set_good),
    # url(r'score/post/bad/(?P<pid>\d+)$', views.post_scoring.set_bad),
)
