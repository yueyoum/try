# -*- coding: utf-8 -*-
import json
from functools import wraps


from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.paginator import Paginator
# from django.db.models import F

from config import (
    redis_client,
    UPDATE_CHILD_COUNT_UNTIL,
    MAX_FORK_AMOUNT,
    MAX_ITEMS,
    MAX_HEADERS,
    MAX_TITLE_LENGTH,
    MAX_CONTENT_LENGTH,
)

from notifyme import send_notify

from .models import HeadPost, BodyPost





def post_guard(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if not request.siteuser or request.method != 'POST':
            return HttpResponse(status=403)
        return func(request, *args, **kwargs)
    return deco



def set_post_child_count(posts):
    pipe = redis_client.pipeline()
    for p in posts:
        pipe.hget('childcount', p.id)
    child_counts = pipe.execute()

    for index, cc in enumerate(child_counts):
        setattr(posts[index], 'child_counts', int(cc) if cc else 0)


# def set_post_score_status(pobj, uid):
#     if uid:
#         setattr(pobj, 'scored_good', redis_client.sismember('good.{0}'.format(uid), pobj.id))
#         setattr(pobj, 'scored_bad', redis_client.sismember('bad.{0}'.format(uid), pobj.id))
#         setattr(pobj, 'scored', pobj.scored_good or pobj.scored_bad)
#     else:
#         setattr(pobj, 'scored_good', False)
#         setattr(pobj, 'scored_bad', False)
#         setattr(pobj, 'scored', False)


def get_body_lists(uid, start_id, length=MAX_ITEMS):
    result = [] 
    level_label = None
    for i in xrange(length):
        body = BodyPost.objects.get(id=start_id)
        forks = BodyPost.objects.filter(parent_id=start_id)
        forks_count = forks.count()
        setattr(body, 'can_fork', forks_count < MAX_FORK_AMOUNT)
        if forks_count == 0:
            # 到这里就结束了，后面没有跟帖了
            setattr(body, 'post_forks', [])
            setattr(body, 'level_label', body.level)
            result.append(body)
            return result

        if forks_count == 1:
            # 没有分支，只有一个跟帖
            setattr(body, 'post_forks', [])
            setattr(body, 'level_label', body.level)
            body_forks = forks
        else:
            # 有多个分支，首先根据跟帖数排序
            body_forks = list(forks)
            set_post_child_count(body_forks)
            body_forks.sort(key=lambda b: b.child_counts, reverse=True)
            # for index, b in enumerate(body_forks):
            #     setattr(b, 'level_label', '{0}{1}'.format(b.level, ALPHABET[index]))
            for index in range(len(body_forks)):
                setattr(body_forks[index], 'level_label', '{0}{1}'.format(body_forks[index].level, ALPHABET[index]))
            setattr(body, 'post_forks', body_forks[1:])
            if level_label:
                setattr(body, 'level_label', level_label)
            else:
                setattr(body, 'level_label', body.level)
            level_label = body_forks[0].level_label

        result.append(body)
        start_id = body_forks[0].id

    return result



ALPHABET = [chr(i) for i in range(97, 123)]
def _tree_struct(head_id, head):
    children = BodyPost.objects.filter(parent_id=head_id).values_list('id')
    if not children:
        return

    children_ids = [c[0] for c in children]
    if len(children_ids) == 1:
        x = {'id': children_ids[0], 'name': ' ', 'data': {'b': ''}, 'children': []}
        head['children'].append(x)
        _tree_struct(children_ids[0], x)
    else:
        for index, cid in enumerate(children_ids):
            x = {'id': cid, 'name': '', 'data': {'b': ALPHABET[index]}, 'children': []}
            head['children'].append(x)
            _tree_struct(cid, x)



def tree_struct(request, head_id):
    res = {'id': head_id, 'name': '', 'data': {'b': ''}, 'children': []}
    _tree_struct(head_id, res)
    return HttpResponse(json.dumps(res), mimetype='application/json')





@post_guard
def post_new_head(request):
    """发布新的开头"""
    title = request.POST.get('title', None)
    content = request.POST.get('content', None)

    if not title or not content:
        res = {'ok': False, 'msg': '请填写标题和内容'}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    if len(title) > MAX_TITLE_LENGTH or len(content) > MAX_CONTENT_LENGTH:
        res = {'ok': False, 'msg': '标题或内容太长了'}
        return HttpResponse(json.dumps(res), mimetype='application/json')


    if HeadPost.objects.filter(title=title).exists():
        res = {'ok': False, 'msg': '标题已存在，换一个吧'}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    # check done, save it

    body = BodyPost.objects.create(
        user=request.siteuser,
        content=content,
        posted_at=timezone.now(),
        level=1,
    )

    HeadPost.objects.create(
        id=body.id,
        user=request.siteuser,
        title=title,
        posted_at=timezone.now(),
        updated_at=timezone.now(),
    )

    url = reverse('show_post', kwargs={'post_id': body.id})
    res = {'ok': True, 'msg': url}
    return HttpResponse(json.dumps(res), mimetype='application/json')


@post_guard
def post_new_body(request):
    """发布新的跟帖"""
    head_id = request.POST.get('head_id', None)
    parent_id = request.POST.get('parent_id', None)
    content = request.POST.get('content', None)
    item_last = request.POST.get('item_last', 0) == '1'

    if not content:
        res = {'ok': False, 'msg': '填写内容啊'}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    if len(content) > MAX_CONTENT_LENGTH:
        res = {'ok': False, 'msg': '内容太长了'}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    try:
        head_id = int(head_id)
        parent_id = int(parent_id)

        if not HeadPost.objects.filter(id=head_id).exists():
            res = {'ok': False, 'msg': '非法操作'}
            return HttpResponse(json.dumps(res), mimetype='application/json')

        if BodyPost.objects.filter(parent_id=parent_id).count() >= MAX_FORK_AMOUNT:
            res = {'ok': False, 'msg': '此处已到分支上限，无法添加分支'}
            return HttpResponse(json.dumps(res), mimetype='application/json')

        parent_level = BodyPost.objects.get(id=parent_id).level
        new_body = BodyPost.objects.create(
            user=request.siteuser,
            head_id=head_id,
            parent_id=parent_id,
            content=content,
            posted_at=timezone.now(),
            level=parent_level+1,
        )
    except Exception as e:
        print 'Error:', e
        res = {'ok': False, 'msg': '发生错误，待会再试'}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    # 设置redis中的 parent 和 childcount
    redis_client.hset('parent', new_body.id, parent_id)
    head_child_count = redis_client.hget('childcount', head_id)
    head_child_count = int(head_child_count) if head_child_count else 0
    if head_child_count < UPDATE_CHILD_COUNT_UNTIL:
        redis_client.doeval('set_child_count', 2, 'parent', 'childcount', new_body.id)
    else:
        redis_client.hincrby('childcount', head_id, 1)

    HeadPost.objects.filter(id=head_id).update(updated_at=timezone.now())


    if BodyPost.objects.get(id=parent_id).user.id != request.siteuser.id:
        # 自己跟自己，不用发消息
        url = reverse('show_post', kwargs={'post_id': parent_id})
        title = HeadPost.objects.get(id=head_id).title
        user = BodyPost.objects.get(id=parent_id).user
        send_notify(user, parent_id, url, u'{0} 你的帖子后有人跟帖'.format(title))

    setattr(new_body, 'child_counts', 0)
    setattr(new_body, 'can_fork', True)
    if item_last:
        tpl = 'one_body.html'
        ctx = {'item': new_body, 'request': request}
    else:
        tpl = 'one_fork.html'
        ctx = {'fork': new_body}

    t = loader.get_template(tpl)
    html = t.render(Context(ctx))

    res = {'ok': True, 'last': item_last, 'msg': html, 'itemid': new_body.id}
    return HttpResponse(json.dumps(res), mimetype='application/json')




def show_post(request, post_id):
    """展示post_id及其后续的posts"""
    uid = request.siteuser.id if request.siteuser else 0
    try:
        head_id = BodyPost.objects.get(id=post_id).head
        title = HeadPost.objects.get(id=head_id).title
    except:
        raise Http404

    posts = get_body_lists(uid, post_id)
    set_post_child_count(posts)


    data = {
        'title': title,
        'head_id': head_id,
        'start_id': post_id,
        'items': posts,
        'next_start_id': posts[-1].id,
        'next_body_counts': posts[-1].child_counts,
    }
    return render_to_response(
        'show_post.html',
        data,
        context_instance=RequestContext(request)
    )





def index(request, p):
    """首页，取HeadPost"""
    posts = HeadPost.objects.all().order_by('-updated_at')
    page_list = Paginator(posts, MAX_HEADERS)

    p = int(p)
    if p < 1 or p > page_list.num_pages:
        raise Http404
    page = page_list.page(p)
    items = page.object_list

    set_post_child_count(items)
    data = {
        'items': items,
        'previous_link': False,
        'next_link': False,
    }

    if page.has_previous():
        data['previous_link'] = '/p/{0}'.format(page.previous_page_number())
    if page.has_next():
        data['next_link'] = '/p/{0}'.format(page.next_page_number())

    return render_to_response(
            'index.html',
            data,
            context_instance=RequestContext(request)
        )



# redis scheme
# good.<uid>: set  保存此uid打过good的所有post id
# bad.<uid>: set   保存此uid打过bad的所有post id


# def _scoring_guard(func):
#     @wraps(func)
#     def deco(self, request, *args, **kwargs):
#         if not request.siteuser or request.method != 'POST':
#             return self.response_nothing()
#         return func(self, request, *args, **kwargs)
#     return deco


# class PostScoring(object):
#     def __init__(self, redis_client):
#         self.r = redis_client

#     def has_scored(self, uid, pid):
#         if self.r.sismember('good.{0}'.format(uid), pid):
#             return True

#         if self.r.sismember('bad.{0}'.format(uid), pid):
#             return True

#         return False


#     def post_exist(self, pid):
#         return BodyPost.objects.filter(id=pid)[:1].exists()


#     def response_ok(self):
#         return HttpResponse(json.dumps(1), mimetype='application/json')

#     def response_nothing(self):
#         return HttpResponse(json.dumps(0), mimetype='application/json')


#     @_scoring_guard
#     def set_good(self, request, pid):
#         uid = request.siteuser.id
#         if not self.post_exist(pid) or self.has_scored(uid, pid):
#             return self.response_nothing()

#         self.r.sadd('good.{0}'.format(uid), pid)
#         BodyPost.objects.filter(id=pid).update(good=F('good')+1)
#         return self.response_ok()


#     @_scoring_guard
#     def set_bad(self, request, pid):
#         uid = request.siteuser.id
#         if not self.post_exist(pid) or self.has_scored(uid, pid):
#             return self.response_nothing()

#         self.r.sadd('bad.{0}'.format(uid), pid)
#         BodyPost.objects.filter(id=pid).update(bad=F('bad')+1)
#         return self.response_ok()


# post_scoring = PostScoring(redis_client)
