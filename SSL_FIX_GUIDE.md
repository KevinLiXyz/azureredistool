# SSL连接错误解决指南

## 问题描述
当您遇到以下错误时：
```
连接错误
未知错误: AbstractConnection.__init__() got an unexpected keyword argument 'ssl'
```

这是因为不同版本的Redis Python库对SSL参数的处理方式不同。

## 🔧 解决方案

### 方案 1: 使用自动修复工具 (推荐)

1. **运行SSL连接测试**:
   ```bash
   python test_ssl_connection.py
   ```
   
2. **运行修复工具**:
   ```bash
   python fix_redis_ssl.py
   ```

3. **运行诊断工具** (如果问题仍存在):
   ```bash
   python diagnose_redis.py
   ```

### 方案 2: 手动修复Redis版本

1. **卸载当前Redis包**:
   ```bash
   pip uninstall redis
   ```

2. **安装兼容版本**:
   ```bash
   pip install redis>=4.5.0,<6.0.0
   ```
   
3. **或者安装特定稳定版本**:
   ```bash
   pip install redis==4.5.4
   ```

### 方案 3: 临时禁用SSL (测试用)

1. 在Azure Redis管理工具中：
   - 取消勾选"使用 SSL"选项
   - 将端口改为 `6379`
   - 点击连接

2. **注意**: 这种方法仅适用于测试环境，生产环境必须使用SSL

### 方案 4: 检查环境冲突

1. **检查是否有多个Python环境**:
   ```bash
   where python
   pip list | findstr redis
   ```

2. **清理并重新安装**:
   ```bash
   pip cache purge
   pip uninstall redis -y
   pip install redis==4.5.4
   ```

## 📋 验证修复

运行以下命令验证修复是否成功：

```bash
python test_ssl_connection.py
```

如果看到 "✅ 连接对象创建成功!"，说明问题已解决。

## 🎯 版本兼容性

| Redis版本 | SSL支持 | 推荐使用 |
|-----------|---------|----------|
| 6.4.0+    | 需要特殊配置 | ❌ |
| 5.0.x     | 完全支持 | ✅ |
| 4.5.x     | 完全支持 | ✅ 推荐 |
| < 4.0     | 不支持 | ❌ |

## 🚀 最佳实践

1. **推荐版本**: `redis==4.5.4`
2. **生产环境**: 始终使用SSL连接
3. **测试环境**: 可临时禁用SSL进行调试
4. **版本锁定**: 在requirements.txt中锁定Redis版本

## 📞 如果问题仍然存在

1. 检查网络连接
2. 验证Azure Redis服务状态
3. 确认访问密钥正确
4. 查看Azure Redis服务的SSL/TLS设置
5. 联系系统管理员检查防火墙设置

## 🔍 相关文件

- `azure_redis_manager.py` - 主应用程序（已修复SSL兼容性）
- `test_ssl_connection.py` - SSL连接测试工具
- `fix_redis_ssl.py` - 自动修复工具
- `diagnose_redis.py` - 详细诊断工具
- `redis_connection_fixed.py` - 兼容的连接代码示例
