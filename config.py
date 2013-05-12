# -*- coding: utf-8 -*-
import redis


# Head 后面有多少跟帖后就不再更新 Body 的跟帖数量
UPDATE_CHILD_COUNT_UNTIL = 1000

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379


redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
redis_client = redis.Redis(connection_pool=redis_pool)

