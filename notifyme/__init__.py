# -*- coding: utf-8 -*-

from .models import NotifyMe

def send_notify(user, sign, link, content):
    if NotifyMe.objects.filter(user=user, sign=sign).exists():
        return

    NotifyMe.objects.create(
        user=user,
        sign=sign,
        link=link,
        content=content
    )
