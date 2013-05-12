# -*- coding: utf-8 -*-
import os
import datetime
import json
from functools import wraps


from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import F
from django.conf import settings

from config import redis_client, UPDATE_CHILD_COUNT_UNTIL

from .models import HeadPost, BodyPost


with open(os.path.join(settings.PROJECT_PATH, 'utils', 'set_child_count.lua'), 'r') as f:
    set_child_count_script = f.read()


def post_test(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if not request.siteuser or request.method != 'POST':
            return HttpResponse(status=403)
        return func(request, *args, **kwargs)
    return deco



def _scoring_guard(func):
    @wraps(func)
    def deco(self, request, *args, **kwargs):
        if not request.siteuser or request.method != 'POST':
            return self.response_nothing()
        return func(self, request, *args, **kwargs)
    return deco


def set_post_child_count(posts):
    pipe = redis_client.pipeline()
    for p in posts:
        pipe.hget('childcount', p.id)
    child_counts = pipe.execute()

    for index, cc in enumerate(child_counts):
        setattr(posts[index], 'child_counts', int(cc) if cc else 0)


def set_post_score_status(pobj, uid):
    if uid:
        setattr(pobj, 'scored_good', redis_client.sismember('good.{0}'.format(uid), pobj.id))
        setattr(pobj, 'scored_bad', redis_client.sismember('bad.{0}'.format(uid), pobj.id))
        setattr(pobj, 'scored', pobj.scored_good or pobj.scored_bad)
    else:
        setattr(pobj, 'scored_good', False)
        setattr(pobj, 'scored_bad', False)
        setattr(pobj, 'scored', False)


def get_body_lists(uid, start_id, length=20):
    result = []
    for i in xrange(length):
        body = BodyPost.objects.get(id=start_id)
        set_post_score_status(body, uid)
        forks = BodyPost.objects.filter(parent_id=start_id)
        forks_count = forks.count()
        if forks_count == 0:
            # 到这里就结束了，后面没有跟帖了
            setattr(body, 'post_forks', [])
            result.append(body)
            break

        if forks_count == 1:
            # 没有分支，只有一个跟帖
            setattr(body, 'post_forks', [])
            body_forks = forks
        else:
            # 有多个分支，首先根据跟帖数排序
            body_forks = []
            for _f in forks:
                set_post_score_status(_f, uid)
                body_forks.append(_f)

            set_post_child_count(body_forks)
            body_forks.sort(key=lambda b: b.child_counts, reverse=True)
            setattr(body, 'post_forks', body_forks[1:])

        result.append(body)
        start_id = body_forks[0].id

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

        new_body = BodyPost.objects.create(
            user=request.siteuser,
            head_id=head_id,
            parent_id = parent_id,
            content = content
        )
    except Exception as e:
        print 'Error:', e
        res = {'ok': False, 'msg': '发生错误，待会再试'}
        return HttpResponse(json.dumps(res), mimetype='applicatioin/json')

    # 设置redis中的 parent 和 childcount
    redis_client.hset('parent', new_body.id, parent_id)
    head_child_count = redis_client.hget('childcount', head_id)
    head_child_count = int(head_child_count) if head_child_count else 0
    if head_child_count < UPDATE_CHILD_COUNT_UNTIL:
        redis_client.eval(set_child_count_script, 2, 'parent', 'childcount', new_body.id)
    else:
        redis_client.hincrby('childcount', head_id, 1)

    #HeadPost.objects.filter(id=head_id).update(body_count=F('body_count')+1,
                                               #updated_at=datetime.datetime.now())
    HeadPost.objects.filter(id=head_id).update(updated_at=datetime.datetime.now())


    url = reverse('show_post', kwargs={'post_id': parent_id})
    res = {'ok': True, 'msg': url}
    return HttpResponse(json.dumps(res), mimetype='applicatioin/json')




def show_post(request, post_id):
    """展示post_id及其后续的posts"""
    uid = request.siteuser.id if request.siteuser else 0
    head_id = BodyPost.objects.get(id=post_id).head
    title = HeadPost.objects.get(id=head_id).title

    posts = get_body_lists(uid, post_id)
    set_post_child_count(posts)


    data = {
        'is_head': False,
        'title': title,
        'head_id': head_id,
        'items': posts,
    }
    return render_to_response(
        'show_post.html',
        data,
        context_instance = RequestContext(request)
    )





def index(request):
    """首页，取HeadPost"""
    posts = HeadPost.objects.all().order_by('-updated_at')

    uid = request.siteuser.id if request.siteuser else 0
    items = []
    for p in posts:
        set_post_score_status(p, uid)
        setattr(p, 'post_forks', False)
        items.append(p)

    set_post_child_count(items)

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
# bad.<uid>: set   保存此uid打过bad的所有post id


class PostScoring(object):
    def __init__(self, redis_client):
        self.r = redis_client
        print 'PostScoring init'

    def has_scored(self, uid, pid):
        if self.r.sismember('good.{0}'.format(uid), pid):
            return True

        if self.r.sismember('bad.{0}'.format(uid), pid):
            return True

        return False


    def post_exist(self, pid):
        return BodyPost.objects.filter(id=pid)[:1].exists()


    def response_ok(self):
        return HttpResponse(json.dumps(1), mimetype='applicatioin/json')

    def response_nothing(self):
        return HttpResponse(json.dumps(0), mimetype='applicatioin/json')


    @_scoring_guard
    def set_good(self, request, pid):
        uid = request.siteuser.id
        if not self.post_exist(pid) or self.has_scored(uid, pid):
            return self.response_nothing()

        self.r.sadd('good.{0}'.format(uid), pid)
        BodyPost.objects.filter(id=pid).update(good=F('good')+1)
        return self.response_ok()


    @_scoring_guard
    def set_bad(self, request, pid):
        uid = request.siteuser.id
        if not self.post_exist(pid) or self.has_scored(uid, pid):
            return self.response_nothing()

        self.r.sadd('bad.{0}'.format(uid), pid)
        BodyPost.objects.filter(id=pid).update(bad=F('bad')+1)
        return self.response_ok()


post_scoring = PostScoring(redis_client)

