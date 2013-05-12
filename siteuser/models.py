# -*- coding: utf-8 -*-
import os

from django.db import models

from upload_avatar.signals import avatar_crop_done
from upload_avatar.app_settings import (
    UPLOAD_AVATAR_URL_PREFIX_CROPPED,
    DEFAULT_AVATAR,
    UPLOAD_AVATAR_AVATAR_ROOT
)


class SiteUserManager(models.Manager):
    def create(self, is_social, **kwargs):
        if 'user' not in kwargs and 'user_id' not in kwargs:
            siteuser_kwargs = {
                'is_social': is_social,
                'username': kwargs.pop('username'),
            }
            if 'avatar_url' in kwargs:
                siteuser_kwargs['avatar_url'] = kwargs.pop('avatar_url')
            user = SiteUser.objects.create(**siteuser_kwargs)
            kwargs['user_id'] = user.id

        return super(SiteUserManager, self).create(**kwargs)


class SocialUserManager(SiteUserManager):
    def create(self, **kwargs):
        return super(SocialUserManager, self).create(True, **kwargs)


class InnerUserManager(SiteUserManager):
    def create(self, **kwargs):
        return super(InnerUserManager, self).create(False, **kwargs)


class SocialUser(models.Model):
    user = models.OneToOneField('SiteUser', related_name='social_user')
    site_uid = models.CharField(max_length=128)
    site_id = models.IntegerField()

    objects = SocialUserManager()

    class Meta:
        unique_together = (('site_uid', 'site_id'),)


class InnerUser(models.Model):
    user = models.OneToOneField('SiteUser', related_name='inner_user')
    email = models.CharField(max_length=128, unique=True)
    passwd = models.CharField(max_length=40)

    objects = InnerUserManager()



class SiteUser(models.Model):
    is_social = models.BooleanField()
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    sign = models.CharField(max_length=24, blank=True)

    username = models.CharField(max_length=32)
    # avatar_url for social user
    avatar_url = models.CharField(max_length=255, blank=True)
    # avatar_name for inner user uploaded avatar
    avatar_name = models.CharField(max_length=64, blank=True)

    score = models.IntegerField(default=0)
    head_count = models.IntegerField(default=0)

    def __unicode__(self):
        return u'<SiteUser %d>' % self.id


    @property
    def avatar(self):
        if not self.avatar_url and not self.avatar_name:
            return UPLOAD_AVATAR_URL_PREFIX_CROPPED + DEFAULT_AVATAR
        if self.is_social:
            return self.avatar_url
        return UPLOAD_AVATAR_URL_PREFIX_CROPPED + self.avatar_name


def _save_avatar_in_db(sender, uid, avatar_name, **kwargs):
    if not SiteUser.objects.filter(id=uid, is_social=False).exists():
        pass

    old_avatar_name = SiteUser.objects.get(id=uid).avatar_name
    if old_avatar_name:
        _path = os.path.join(UPLOAD_AVATAR_AVATAR_ROOT, old_avatar_name)
        try:
            os.unlink(_path)
        except:
            pass

    SiteUser.objects.filter(id=uid).update(avatar_name=avatar_name)


avatar_crop_done.connect(_save_avatar_in_db)

