# -*- coding: utf-8 -*-
import json
from functools import wraps

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from .models import InnerUser, SiteUser


# 注册，登录，退出等都通过 ajax 的方式进行


class InnerAccoutError(Exception):
    pass

def inner_accout_guard(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if request.method != 'POST':
            ret_data = {
                'ok': False,
                'msg': '禁止此操作'
            }
            return HttpResponse(json.dumps(ret_data), mimetype='application/json')

        try:
            func(request, *args, **kwargs)
        except InnerAccoutError as e:
            ret_data = {
                'ok': False,
                'msg': str(e)
            }
            return HttpResponse(json.dumps(ret_data), mimetype='application/json')

        return HttpResponse(json.dumps({'ok': True}), mimetype='application/json')
    return deco







@inner_accout_guard
def login(request):
    email = request.POST.get('email', None)
    passwd = request.POST.get('passwd', None)


    if not email or not passwd:
        raise InnerAccoutError('请填写email和密码')

    try:
        user = InnerUser.objects.get(email=email)
    except InnerUser.DoesNotExist:
        raise InnerAccoutError('此用户不存在')

    if user.passwd != passwd:
        raise InnerAccoutError('密码错误')

    # done
    request.session['uid'] = user.user.id




@inner_accout_guard
def register(request):
    email = request.POST.get('email', None)
    username = request.POST.get('username', None)
    passwd = request.POST.get('passwd', None)


    if not email or not username or not passwd:
        raise InnerAccoutError('请完整填写注册信息')


    if InnerUser.objects.filter(email=email).exists():
        raise InnerAccoutError('此电子邮件已被占用')

    # FIXME 检测username是否重名？
    user = InnerUser.objects.create(email=email, passwd=passwd, username=username)
    request.session['uid'] = user.id

    # finish


def logout(request):
    try:
        del request.session['uid']
    except:
        pass

    return HttpResponse('', mimetype='application/json')


def account_settings(request):
    return render_to_response('account_settings.html', context_instance=RequestContext(request))



@inner_accout_guard
def set_mysign(request):
    """设置个性签名"""
    mysign = request.POST.get('mysign', None)
    if not mysign:
        raise InnerAccoutError('请填写')

    try:
        SiteUser.objects.filter(id=request.siteuser.id).update(sign=mysign)
    except Exception as e:
        # TODO log e
        raise InnerAccoutError('error...')

    # done.



