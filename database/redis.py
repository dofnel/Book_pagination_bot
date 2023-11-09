from aioredis import Redis

redis = Redis(decode_responses=True)
redis.set_response_callback('hget', int)
redis.set_response_callback('rpush', int)
