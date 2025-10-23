
# 兼容的Redis连接代码
def create_redis_connection(host, port, password, use_ssl=True):
    """创建兼容的Redis连接"""
    import redis
    from redis.connection import ConnectionPool
    
    try:
        # 方法1：尝试新版本SSL参数
        if use_ssl:
            pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                ssl=True,
                ssl_cert_reqs=None,
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=5,
                max_connections=20
            )
        else:
            pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=5,
                max_connections=20
            )
        
        client = redis.Redis(connection_pool=pool)
        return client, "new_version"
        
    except TypeError:
        # 方法2：使用SSL连接类（旧版本兼容）
        if use_ssl:
            pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                connection_class=redis.SSLConnection,
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=5,
                max_connections=20
            )
        else:
            pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=5,
                max_connections=20
            )
        
        client = redis.Redis(connection_pool=pool)
        return client, "old_version"
