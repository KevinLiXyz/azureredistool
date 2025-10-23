
def create_redis_connection_fixed(host, port, password, use_ssl=True):
    """修复后的Redis连接函数"""
    import redis
    from redis.connection import ConnectionPool
    
    # 基础参数
    base_params = {
        'host': host,
        'port': port,
        'password': password,
        'decode_responses': True,
        'socket_timeout': 10,
        'socket_connect_timeout': 5,
        'max_connections': 20
    }
    
    if use_ssl:
        # 尝试多种SSL配置方法
        ssl_configs = [
            # 方法1: 新版本SSL参数
            {**base_params, 'ssl': True, 'ssl_cert_reqs': None},
            
            # 方法2: 只有ssl参数
            {**base_params, 'ssl': True},
            
            # 方法3: 使用SSL连接类
            {**base_params, 'connection_class': redis.SSLConnection},
        ]
        
        for i, config in enumerate(ssl_configs, 1):
            try:
                pool = ConnectionPool(**config)
                client = redis.Redis(connection_pool=pool)
                print(f"SSL方法{i}成功")
                return client
            except Exception as e:
                print(f"SSL方法{i}失败: {e}")
                continue
        
        raise Exception("所有SSL连接方法都失败")
    else:
        # 非SSL连接
        pool = ConnectionPool(**base_params)
        return redis.Redis(connection_pool=pool)
