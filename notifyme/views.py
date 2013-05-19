# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from .models import NotifyMe


def get_notifies(request):
    user = request.siteuser
    if not user:
        return HttpResponse(json.dumps([]), mimetype='application/json')

    notifies = NotifyMe.objects.filter(user=user)

    def _make_html(n):
        return u'<a href="{0}" noti-id="{1}" class="notifyme">{2}</a>'.format(
            n.link, n.id, n.content
        )

    contents = [_make_html(n) for n in notifies]
    return HttpResponse(json.dumps(contents), mimetype='application/json')



def confirm_notify(request):
    def _ret():
        return HttpResponse(json.dumps(''), mimetype='application/json')

    if not request.siteuser or request.method != 'POST':
        return _ret()

    try:
        nid = int(request.POST.get('nid'))
        NotifyMe.objects.filter(id=nid).delete()
    except:
        pass

    return _ret()

