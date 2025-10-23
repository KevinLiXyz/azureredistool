#!/usr/bin/env python3
"""
Redis兼容性检查和修复工具
解决不同Redis版本的SSL连接问题
"""

import sys
import subprocess

def check_redis_version():
    """检查Redis版本"""
    try:
        import redis
        version = redis.__version__
        print(f"当前Redis版本: {version}")
        
        # 检查版本兼容性
        major_version = int(version.split('.')[0])
        
        if major_version >= 5:
            print("✓ Redis版本兼容SSL连接")
            return True, version
        elif major_version == 4:
            print("⚠ Redis版本可能存在SSL兼容性问题")
            return False, version
        else:
            print("✗ Redis版本过旧，建议升级")
            return False, version
            
    except ImportError:
        print("✗ Redis包未安装")
        return False, None
    except Exception as e:
        print(f"✗ 检查版本时出错: {e}")
        return False, None

def test_ssl_connection():
    """测试SSL连接功能"""
    try:
        import redis
        from redis.connection import ConnectionPool
        
        print("测试SSL连接参数...")
        
        # 测试方法1：直接SSL参数
        try:
            pool = ConnectionPool(
                host="test.redis.cache.windows.net",
                port=6380,
                ssl=True,
                ssl_cert_reqs=None,
                decode_responses=True
            )
            print("✓ 方法1：直接SSL参数 - 支持")
            return "direct_ssl"
        except TypeError as e:
            if 'ssl' in str(e):
                print("✗ 方法1：直接SSL参数 - 不支持")
            else:
                print(f"✗ 方法1：其他错误 - {e}")
        
        # 测试方法2：SSL连接类
        try:
            pool = ConnectionPool(
                host="test.redis.cache.windows.net",
                port=6380,
                connection_class=redis.SSLConnection,
                decode_responses=True
            )
            print("✓ 方法2：SSL连接类 - 支持")
            return "ssl_class"
        except Exception as e:
            print(f"✗ 方法2：SSL连接类 - {e}")
        
        # 测试方法3：简单连接
        try:
            client = redis.Redis(
                host="test.redis.cache.windows.net",
                port=6380,
                ssl=True,
                decode_responses=True
            )
            print("✓ 方法3：简单SSL连接 - 支持")
            return "simple_ssl"
        except Exception as e:
            print(f"✗ 方法3：简单SSL连接 - {e}")
        
        return None
        
    except ImportError:
        print("✗ Redis包未安装，无法测试")
        return None

def fix_redis_installation():
    """修复Redis安装"""
    print("\n开始修复Redis安装...")
    
    try:
        # 卸载当前版本
        print("正在卸载当前Redis版本...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "redis", "-y"], 
                      check=False, capture_output=True)
        
        # 安装兼容版本
        print("正在安装兼容的Redis版本...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "redis>=4.5.0,<6.0.0"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Redis安装成功")
            return True
        else:
            print(f"✗ Redis安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 修复过程出错: {e}")
        return False

def create_compatible_connection_code():
    """生成兼容的连接代码"""
    
    compatible_code = '''
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
'''
    
    with open("redis_connection_fix.py", "w", encoding="utf-8") as f:
        f.write(compatible_code)
    
    print("✓ 兼容连接代码已保存到 redis_connection_fix.py")

def main():
    print("Redis SSL 兼容性检查和修复工具")
    print("=" * 50)
    
    # 检查当前版本
    is_compatible, version = check_redis_version()
    
    if not is_compatible and version is None:
        print("\n需要安装Redis包...")
        if fix_redis_installation():
            is_compatible, version = check_redis_version()
    
    # 测试SSL连接
    if version:
        print(f"\n测试SSL连接兼容性...")
        ssl_method = test_ssl_connection()
        
        if ssl_method:
            print(f"✓ 找到兼容的SSL连接方法: {ssl_method}")
        else:
            print("✗ 未找到兼容的SSL连接方法")
            
            # 尝试修复
            answer = input("\n是否尝试重新安装兼容版本的Redis? (y/n): ")
            if answer.lower() == 'y':
                if fix_redis_installation():
                    print("请重新运行此脚本进行测试")
                else:
                    print("修复失败，请手动安装: pip install redis>=4.5.0,<6.0.0")
    
    # 生成兼容代码
    create_compatible_connection_code()
    
    print("\n" + "=" * 50)
    print("检查完成!")
    print("\n建议:")
    print("1. 如果仍有问题，请运行: pip install redis>=4.5.0,<6.0.0")
    print("2. 或者在Azure Redis管理工具中取消勾选SSL选项")
    print("3. 查看 redis_connection_fix.py 了解兼容的连接方法")

if __name__ == "__main__":
    main()
