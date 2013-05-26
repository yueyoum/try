# -*- coding: utf-8 -*-
import os
import hashlib

import redis

from django.conf import settings


# 每页展示多少条head
MAX_HEADERS = 12
# 每页展示多少条body
MAX_ITEMS = 12
# Head 后面有多少跟帖后就不再更新 Body 的跟帖数量
UPDATE_CHILD_COUNT_UNTIL = 1000
# 每个body后面最多有几个分叉
MAX_FORK_AMOUNT = 5

# 标题最大长度
MAX_TITLE_LENGTH = 40
# 内容最大长度
MAX_CONTENT_LENGTH = 255


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379




class MyRedis(redis.Redis):
    def __init__(self, *args, **kwargs):
        super(MyRedis, self).__init__(*args, **kwargs)
        self._script_sha1 = {}

    def doeval(self, script_name, key_nums, *args):
        sha1 = self._script_sha1.get(script_name, None)
        if not sha1:
            with open(os.path.join(settings.PROJECT_PATH, 'luascript', script_name + '.lua'), 'r') as f:
                content = f.read()

            sha1 = hashlib.sha1(content).hexdigest()
            self._script_sha1[script_name] = sha1

        try:
            return self.evalsha(sha1, key_nums, *args)
        except (redis.exceptions.ResponseError, redis.exceptions.NoScriptError):
            return self.eval(content, key_nums, *args)




redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
redis_client = MyRedis(connection_pool=redis_pool)
