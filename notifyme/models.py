# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone


class NotifyMe(models.Model):
    user = models.ForeignKey('siteuser.SiteUser', related_name='notifies')
    sign = models.IntegerField()
    link = models.CharField(max_length=255)
    content = models.TextField()
    noti_at = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
        return u'<NotifyMe %d>' % self.id

    class Meta:
        index_together = [
                    ['user', 'sign'],
                ]


# sign 用来阻止同类型通知重复发送，比如多个人都跟帖了某人
# 此时，某人只要收到一次 “有人跟帖” 这样的通知就行

