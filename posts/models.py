# -*- coding: utf-8 -*-
import datetime

from django.db import models

# from config import redis_client


class HeadPost(models.Model):
    # 故事/段子的开头，body_count记录此故事有多少个延续，将其单独记录是为了方便在首页显示
    user = models.ForeignKey('siteuser.SiteUser', related_name='head_posts')
    title = models.CharField(max_length=40, db_index=True)

    updated_at = models.DateTimeField(default=datetime.datetime.now(), db_index=True)



    def __unicode__(self):
        return u'<HeadPost %d>' % self.id

    @property
    def metaobj(self):
        return BodyPost.objects.get(id=self.id)

    @property
    def content(self):
        obj = getattr(self, '_metaobj', None)
        if not obj:
            obj = self.metaobj
            self._metaobj = obj
        return obj.content

    @property
    def posted_at(self):
        obj = getattr(self, '_metaobj', None)
        if not obj:
            obj = self.metaobj
            self._metaobj = obj
        return obj.posted_at

    @property
    def good(self):
        obj = getattr(self, '_metaobj', None)
        if not obj:
            obj = self.metaobj
            self._metaobj = obj
        return obj.good

    @property
    def bad(self):
        obj = getattr(self, '_metaobj', None)
        if not obj:
            obj = self.metaobj
            self._metaobj = obj
        return obj.bad



class BodyPost(models.Model):
    # 故事的延续，除了顺序延续外，还可以分叉，见下图
    # 这里的head_id仅仅是为了更新head的body_count和updated_at
    # 新加入一个body，根据其parent_id查到head_id，然后增加此head的body_count
    # parent_id表示这个body是哪个body的后续。一个body可以有多个后续body，也就是分叉
    user = models.ForeignKey('siteuser.SiteUser', related_name='body_posts')
    head_id = models.PositiveIntegerField(default=0)
    parent_id = models.PositiveIntegerField(default=0, db_index=True)

    content = models.CharField(max_length=255)
    posted_at = models.DateTimeField(default=datetime.datetime.now(), db_index=True)

    good = models.PositiveIntegerField(default=0)
    bad = models.PositiveIntegerField(default=0)

    # comments_count = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u'<BodyPost %d>' % self.id

    @property
    def head(self):
        return self.head_id if self.head_id else self.id

    @property
    def parent(self):
        return self.parent_id if self.parent_id else self.id





#class Comment(models.Model):
#    # 每个段子都可以评论
#    # 考虑到在右侧要放置广告，所以评论可参考糗百，直接在此段子下面展开收起
#    user = models.ForeignKey('siteuser.SiteUser', related_name='comments')
#    post = models.PositiveIntegerField(db_index=True)
#    content = models.CharField(max_length=255)
#    posted_at = models.DateTimeField(auto_now_add=True)




# head
#   |
# body1 --
#   |    |
# body2 body3
#   |    |
# body4 body5


# 查询过程：
# 1
# 首页排列出各个故事/段子的名字(title)和开头(content)
# 可根据不同方式来排列，比如最新发表，新的进展，最热门……

# 2
# 点击某一个开头，打开新页面 展示这个开头的后续发展
# 固定取20个body，有分支的body特殊表示，默认展现得分最高的分支，大概为这样：

# head
# body1 *
# body2
# body3 *
# ...

# 带星号的表示有分支，在web上高亮显示，当点击body1时，进入新页面，分支展示页面

# body1
#   body2
#   body5
#   body6
#   body7

# 这些分支以得分高低排序

# url设计得大概这样 /posts/<post_id:int>
# 表示此页面从post_id开始，取跟在它后面一定数量个段子



