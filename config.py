# -*- coding: utf-8 -*-
import redis

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379


redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
redis_client = redis.Redis(connection_pool=redis_pool)

