#!/usr/bin/env python3
"""
Redis连接问题诊断工具
专门诊断SSL连接参数问题
"""

def detailed_redis_diagnosis():
    """详细的Redis诊断"""
    print("Redis SSL 连接问题详细诊断")
    print("=" * 50)
    
    try:
        import redis
        print(f"Redis版本: {redis.__version__}")
        
        # 检查Redis内部结构
        print(f"Redis模块路径: {redis.__file__}")
        
        # 检查ConnectionPool
        from redis.connection import ConnectionPool
        print("ConnectionPool 可用")
        
        # 检查SSL相关类
        try:
            from redis.connection import SSLConnection
            print("SSLConnection 类可用")
        except ImportError:
            print("⚠ SSLConnection 类不可用")
        
        # 测试创建连接池的不同方法
        print("\n测试连接池创建方法:")
        
        # 方法1：最基础的连接池
        try:
            pool = ConnectionPool(host="localhost", port=6379)
            print("✓ 基础连接池创建成功")
        except Exception as e:
            print(f"✗ 基础连接池失败: {e}")
        
        # 方法2：带SSL的连接池（新版本）
        try:
            pool = ConnectionPool(
                host="test.redis.cache.windows.net",
                port=6380,
                ssl=True,
                ssl_cert_reqs=None
            )
            print("✓ SSL连接池（新版本）创建成功")
        except Exception as e:
            print(f"✗ SSL连接池（新版本）失败: {e}")
            
        # 方法3：使用SSLConnection类
        try:
            pool = ConnectionPool(
                host="test.redis.cache.windows.net",
                port=6380,
                connection_class=redis.SSLConnection
            )
            print("✓ SSL连接池（连接类）创建成功")
        except Exception as e:
            print(f"✗ SSL连接池（连接类）失败: {e}")
        
        # 检查ConnectionPool的__init__参数
        import inspect
        sig = inspect.signature(ConnectionPool.__init__)
        params = list(sig.parameters.keys())
        print(f"\nConnectionPool.__init__ 支持的参数:")
        for param in params[1:]:  # 跳过self
            print(f"  - {param}")
        
        if 'ssl' in params:
            print("✓ 支持 ssl 参数")
        else:
            print("✗ 不支持 ssl 参数")
            
        # 检查具体的ssl参数类型
        if 'ssl' in params:
            ssl_param = sig.parameters['ssl']
            print(f"ssl 参数详情: {ssl_param}")
        
    except Exception as e:
        print(f"诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

def test_actual_connection():
    """测试实际的连接创建"""
    print("\n" + "=" * 30)
    print("测试实际连接创建")
    print("=" * 30)
    
    try:
        import redis
        from redis.connection import ConnectionPool
        
        # 模拟您的连接参数
        test_configs = [
            {
                "name": "Azure Redis (SSL)",
                "config": {
                    'host': 'test.redis.cache.windows.net',
                    'port': 6380,
                    'password': 'test-password',
                    'ssl': True,
                    'ssl_cert_reqs': None,
                    'decode_responses': True,
                    'socket_timeout': 10,
                    'socket_connect_timeout': 5,
                    'max_connections': 20
                }
            },
            {
                "name": "Azure Redis (无SSL)",
                "config": {
                    'host': 'test.redis.cache.windows.net',
                    'port': 6379,
                    'password': 'test-password',
                    'decode_responses': True,
                    'socket_timeout': 10,
                    'socket_connect_timeout': 5,
                    'max_connections': 20
                }
            }
        ]
        
        for test in test_configs:
            print(f"\n测试: {test['name']}")
            try:
                pool = ConnectionPool(**test['config'])
                client = redis.Redis(connection_pool=pool)
                print(f"✓ {test['name']} - 连接对象创建成功")
            except Exception as e:
                print(f"✗ {test['name']} - 失败: {e}")
                print(f"  错误类型: {type(e).__name__}")
                
    except Exception as e:
        print(f"测试连接时出错: {e}")

def generate_fixed_code():
    """生成修复后的代码"""
    print("\n" + "=" * 30)
    print("生成修复代码")
    print("=" * 30)
    
    fixed_code = '''
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
'''
    
    with open("redis_connection_fixed.py", "w", encoding="utf-8") as f:
        f.write(fixed_code)
    
    print("✓ 修复代码已保存到 redis_connection_fixed.py")

if __name__ == "__main__":
    detailed_redis_diagnosis()
    test_actual_connection()
    generate_fixed_code()
    
    print("\n" + "=" * 50)
    print("诊断完成!")
    print("如果问题仍然存在，请:")
    print("1. 检查是否有多个Redis包版本冲突")
    print("2. 尝试: pip uninstall redis && pip install redis==4.5.4")
    print("3. 在应用中暂时禁用SSL选项进行测试")
