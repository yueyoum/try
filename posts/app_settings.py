# -*- coding:utf-8 -*-

from django.conf import settings

REDIS_HOST = getattr(settings, 'REDIS_HOST', '127.0.0.1')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)

