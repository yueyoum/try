# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


from config import MAX_TITLE_LENGTH, MAX_CONTENT_LENGTH



class HeadPost(models.Model):
    # 故事/段子的开头，body_count记录此故事有多少个延续，将其单独记录是为了方便在首页显示
    user = models.ForeignKey('siteuser.SiteUser', related_name='head_posts')
    title = models.CharField(max_length=MAX_TITLE_LENGTH, db_index=True)

    posted_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(default=timezone.now(), db_index=True)

    def __unicode__(self):
        return u'<HeadPost %d>' % self.id

    @property
    def metaobj(self):
        obj = getattr(self, '_metaobj', None)
        if not obj:
            obj = BodyPost.objects.get(id=self.id)
            self._metaobj = obj
        return obj

    @property
    def content(self):
        return self.metaobj.content



class BodyPost(models.Model):
    # 故事的延续，除了顺序延续外，还可以分叉，见下图
    # 这里的head_id仅仅是为了更新head的updated_at
    # parent_id表示这个body是哪个body的后续。一个body可以有多个后续body，也就是分叉
    user = models.ForeignKey('siteuser.SiteUser', related_name='body_posts')
    head_id = models.PositiveIntegerField(default=0)
    parent_id = models.PositiveIntegerField(default=0, db_index=True)

    content = models.CharField(max_length=MAX_CONTENT_LENGTH)
    posted_at = models.DateTimeField(default=timezone.now())

    level = models.PositiveIntegerField()
    # branch = models.CharField(max_length=1, blank=True)

    # good = models.PositiveIntegerField(default=0)
    # bad = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u'<BodyPost %d>' % self.id

    @property
    def head(self):
        return self.head_id if self.head_id else self.id

    @property
    def parent(self):
        return self.parent_id if self.parent_id else self.id
