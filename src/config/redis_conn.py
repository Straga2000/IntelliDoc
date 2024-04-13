import redis

pool = redis.ConnectionPool(
    host="localhost",
    port="6379"
)

redis_instance = redis.Redis(connection_pool=pool)
