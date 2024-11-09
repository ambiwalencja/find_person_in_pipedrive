import os
import redis

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_DB = int(os.environ.get("REDIS_DB"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_SSL = True

def get_redis_connection():
    return redis.Redis(
                REDIS_HOST, 
                REDIS_PORT, 
                REDIS_DB, 
                password=REDIS_PASSWORD, 
                ssl=True,
                health_check_interval=30)