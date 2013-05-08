# -*- coding: utf-8 -*-

import os
import hashlib
import time
from functools import wraps

from PIL import Image

from django.http import HttpResponse
from django.utils.crypto import get_random_string

from .app_settings import (
    UPLOAD_AVATAR_MAX_SIZE,
    UPLOAD_AVATAR_UPLOAD_ROOT,
    UPLOAD_AVATAR_AVATAR_ROOT,
    UPLOAD_AVATAR_URL_PREFIX_ORIGINAL,
    UPLOAD_AVATAR_RESIZE_SIZE,
    UPLOAD_AVATAR_SAVE_FORMAT,
    UPLOAD_AVATAR_SAVE_QUALITY,
    UPLOAD_AVATAR_DELETE_ORIGINAL_AFTER_CROP,
)




from .signals import avatar_crop_done
from .models import UploadedImage


border_size = 300


test_func = lambda request: request.method == 'POST' and request.siteuser
get_uid = lambda request: request.siteuser.id




class UploadAvatarError(Exception):
    pass



def protected(func):
    @wraps(func)
    def deco(request, *args, **kwargs):
        if not test_func(request):
            return HttpResponse(
                "<script>window.parent.upload_avatar_error('%s')</script>" % '禁止进行此操作'
            )
        try:
            return func(request, *args, **kwargs)
        except UploadAvatarError as e:
            return HttpResponse(
                "<script>window.parent.upload_avatar_error('%s')</script>" % e
            )
    return deco


@protected
def upload_avatar(request):
    try:
        uploaded_file = request.FILES['uploadavatarfile']
    except KeyError:
        raise UploadAvatarError('请正确上传图片')

    if uploaded_file.size > UPLOAD_AVATAR_MAX_SIZE:
        raise UploadAvatarError('图片不能大于3MB')


    name, ext = os.path.splitext(uploaded_file.name)
    new_name = hashlib.md5(
        '%s%f' % (get_random_string(), time.time())
    ).hexdigest()
    new_name = '%s%s' % (new_name, ext.lower())

    fpath = os.path.join(UPLOAD_AVATAR_UPLOAD_ROOT, new_name)

    with open(fpath, 'w') as f:
        for c in uploaded_file.chunks(10240):
            f.write(c)

    try:
        Image.open(fpath)
    except IOError:
        try:
            os.unlink(fpath)
        except:
            pass
        raise UploadAvatarError('请正确上传图片')

    # uploaed image has been saved on disk, now save it's name in db
    if UploadedImage.objects.filter(uid=get_uid(request)).exists():
        _obj = UploadedImage.objects.get(uid=get_uid(request))
        _obj.delete_image()
        UploadedImage.objects.filter(uid=get_uid(request)).update(image=new_name)
    else:
        UploadedImage.objects.create(uid=get_uid(request), image=new_name)

    return HttpResponse(
        "<script>window.parent.upload_avatar_success('%s')</script>" % (
            UPLOAD_AVATAR_URL_PREFIX_ORIGINAL + new_name
        )
    )


@protected
def crop_avatar(request):
    try:
        upim = UploadedImage.objects.get(uid=get_uid(request))
    except UploadedImage.DoesNotExist:
        raise UploadAvatarError('请先上传图片')

    image_orig = upim.get_image_path()
    if not image_orig:
        raise UploadAvatarError('请先上传图片')

    try:
        x1 = int(float(request.POST['x1']))
        y1 = int(float(request.POST['y1']))
        x2 = int(float(request.POST['x2']))
        y2 = int(float(request.POST['y2']))
    except:
        raise UploadAvatarError('发生错误，请稍后重试')


    try:
        orig = Image.open(image_orig)
    except IOError:
        raise UploadAvatarError('发生错误，请重新上传图片')

    orig_w, orig_h = orig.size
    if orig_w <= border_size and orig_h <= border_size:
        ratio = 1
    else:
        if orig_w > orig_h:
            ratio = float(orig_w) / border_size
        else:
            ratio = float(orig_h) / border_size

    box = [int(x * ratio) for x in [x1, y1, x2, y2]]
    avatar = orig.crop(box)
    avatar_name, _ = os.path.splitext(upim.image)


    size = UPLOAD_AVATAR_RESIZE_SIZE
    try:
        res = avatar.resize((size, size), Image.ANTIALIAS)
        res_name = '%s-%d.%s' % (avatar_name, size, UPLOAD_AVATAR_SAVE_FORMAT)
        res_path = os.path.join(UPLOAD_AVATAR_AVATAR_ROOT, res_name)
        res.save(res_path, UPLOAD_AVATAR_SAVE_FORMAT, quality=UPLOAD_AVATAR_SAVE_QUALITY)
    except:
        raise UploadAvatarError('发生错误，请稍后重试')


    avatar_crop_done.send(sender = None,
                          uid = get_uid(request),
                          avatar_name = res_name,
                          dispatch_uid = 'upload_avatar_crop_done'
                          )

    if UPLOAD_AVATAR_DELETE_ORIGINAL_AFTER_CROP:
        upim.delete()

    return HttpResponse(
        "<script>window.parent.crop_avatar_success('%s')</script>"  % '成功'
    )

