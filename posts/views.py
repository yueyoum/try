# -*- coding: utf-8 -*-
import datetime
import json
from functools import wraps

import redis

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import F


from .models import HeadPost, BodyPost
from .app_settings import REDIS_HOST, REDIS_PORT


redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
redis_client = redis.Redis(connection_pool=redis_pool)



def post_test(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if not request.siteuser or request.method != 'POST':
            return HttpResponse(status=403)
        return func(request, *args, **kwargs)
    return deco

def get_body_lists(start_id, length=20):
    result = []
    for i in xrange(length):
        body = BodyPost.objects.get(id=start_id)
        forks = BodyPost.objects.filter(parent_id=start_id).order_by('good')
        forks_count = forks.count()
        if forks_count == 0:
            # 到这里就结束了，后面没有跟帖了
            setattr(body, 'post_forks', [])
            result.append(body)
            break

        if forks_count == 1:
            # 没有分支，只有一个跟帖
            setattr(body, 'post_forks', [])
        else:
            setattr(body, 'post_forks', forks[1:])

        result.append(body)
        start_id = forks[0].id

    return result



@post_test
def post_new_head(request):
    """发布新的开头"""
    title = request.POST.get('title', None)
    content = request.POST.get('content', None)

    if not title or not content:
        res = {'ok': False, 'msg': '请填写标题和内容'}
        return HttpResponse(json.dumps(res), mimetype='applicatioin/json')

    # TODO title length and content length

    if HeadPost.objects.filter(title=title).exists():
        res = {'ok': False, 'msg': '标题已存在，换一个吧'}
        return HttpResponse(json.dumps(res), mimetype='applicatioin/json')

    # check done, save it

    body = BodyPost.objects.create(
        user=request.siteuser,
        content = content,
    )

    HeadPost.objects.create(
        id = body.id,
        user = request.siteuser,
        title=title,
    )


    url = reverse('show_post', kwargs={'post_id': body.id})
    res = {'ok': True, 'msg': url}
    return HttpResponse(json.dumps(res), mimetype='applicatioin/json')



@post_test
def post_new_body(request):
    """发布新的跟帖"""
    head_id = request.POST.get('head_id', None)
    parent_id = request.POST.get('parent_id', None)
    content = request.POST.get('content', None)


    if not content:
        res = {'ok': False, 'msg': '填写内容啊'}
        return HttpResponse(json.dumps(res), mimetype='applicatioin/json')


    try:
        head_id = int(head_id)
        parent_id = int(parent_id)

        if not HeadPost.objects.filter(id=head_id).exists():
            res = {'ok': False, 'msg': '非法操作'}
            return HttpResponse(json.dumps(res), mimetype='applicatioin/json')

        BodyPost.objects.create(
            user=request.siteuser,
            head_id=head_id,
            parent_id = parent_id,
            content = content
        )
    except Exception as e:
        print 'Error:', e
        res = {'ok': False, 'msg': '发生错误，待会再试'}
        return HttpResponse(json.dumps(res), mimetype='applicatioin/json')

    HeadPost.objects.filter(id=head_id).update(body_count=F('body_count')+1,
                                               updated_at=datetime.datetime.now())


    url = reverse('show_post', kwargs={'post_id': parent_id})
    res = {'ok': True, 'msg': url}
    return HttpResponse(json.dumps(res), mimetype='applicatioin/json')




def show_post(request, post_id):
    """展示post_id及其后续的posts"""
    head_id = BodyPost.objects.get(id=post_id).head
    title = HeadPost.objects.get(id=head_id).title
    posts = get_body_lists(post_id)

    uid = request.siteuser.id
    items = []
    for p in posts:
        setattr(p, 'score_good', redis_client.sismember('good.{0}'.format(uid), p.id))
        setattr(p, 'score_bad', redis_client.sismember('bag.{0}'.format(uid), p.id))
        setattr(p, 'scored', p.score_good or p.score_bad)
        items.append(p)

    data = {
        'is_head': False,
        'title': title,
        'head_id': head_id,
        'items': items,
    }
    return render_to_response(
        'show_post.html',
        data,
        context_instance = RequestContext(request)
    )





def index(request):
    """首页，取HeadPost"""
    posts = HeadPost.objects.all().order_by('-updated_at')
    # items = ({'post': p} for p in posts)

    # uid = request.siteuser.id

    items = []
    for p in posts:
        setattr(p, 'post_forks', False)
        items.append(p)

    data = {
        'is_head': True,
        'items': items,
    }
    return render_to_response(
            'index.html',
            data,
            context_instance=RequestContext(request)
            )



# redis scheme
# good.<uid>: set  保存此uid打过good的所有post id
# bag.<uid>: set   保存此uid打过bad的所有post id

@post_test
def set_good(request, post_id):
    """给帖子good"""
    if not BodyPost.objects.filter(id=post_id)[:1].exists():
        return HttpResponse(json.dumps(0), mimetype='applicatioin/json')


    uid = request.siteuser.id
    if redis_client.sismember('good.{0}'.format(uid), post_id):
        return HttpResponse(json.dumps(0), mimetype='applicatioin/json')

    redis_client.sadd('good.{0}'.format(uid), post_id)

    BodyPost.objects.filter(id=post_id).update(good=F('good')+1)
    return HttpResponse(json.dumps(1), mimetype='applicatioin/json')


@post_test
def set_bad(request, post_id):
    """给帖子bad"""
    if not BodyPost.objects.filter(id=post_id)[:1].exists():
        return HttpResponse(json.dumps(0), mimetype='applicatioin/json')


    uid = request.siteuser.id
    if redis_client.sismember('bad.{0}'.format(uid), post_id):
        return HttpResponse(json.dumps(0), mimetype='applicatioin/json')

    redis_client.sadd('bad.{0}'.format(uid), post_id)

    BodyPost.objects.filter(id=post_id).update(bad=F('bad')+1)
    return HttpResponse(json.dumps(1), mimetype='applicatioin/json')


