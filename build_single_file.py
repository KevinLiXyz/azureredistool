#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Redis Manager - 优化单文件打包脚本
生成最小化的独立可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 55)
    print("    Azure Redis Manager - 单文件打包工具")
    print("=" * 55)
    print()

def clean_build_files():
    """清理之前的构建文件"""
    print("🧹 正在清理构建文件...")
    
    directories_to_clean = ['dist', 'build', '__pycache__']
    files_to_clean = ['*.spec']
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"✅ 已删除 {directory}/")
    
    # 删除spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"✅ 已删除 {spec_file}")

def build_single_file():
    """构建优化的单文件可执行文件"""
    print("\n🚀 开始单文件打包...")
    print("正在生成最优化的独立exe文件...")
    print("这可能需要3-5分钟，请耐心等待...\n")
    
    # 优化的PyInstaller命令参数
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        
        # 基本打包选项
        '--onefile',                         # 打包成单个文件
        '--windowed',                        # 无控制台窗口（GUI程序）
        '--name', 'AzureRedisManager',       # 可执行文件名
        '--distpath', 'dist',                # 输出目录
        '--workpath', 'build',               # 工作目录
        '--specpath', '.',                   # spec文件位置
        '--clean',                           # 清理临时文件
        
        # 优化选项
        '--optimize', '2',                   # Python字节码优化级别
        '--strip',                           # 去除调试符号
        '--upx-dir', 'upx',                  # UPX压缩（如果可用）
        
        # 必需的隐藏导入
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.simpledialog',
        '--hidden-import', 'redis',
        '--hidden-import', 'redis.connection',
        '--hidden-import', 'redis.exceptions',
        '--hidden-import', 'threading',
        '--hidden-import', 'queue',
        '--hidden-import', 'socket',
        '--hidden-import', 'ssl',
        '--hidden-import', 'datetime',
        '--hidden-import', 'time',
        '--hidden-import', 'json',
        '--hidden-import', 'logging',
        
        # 排除不需要的模块（减小文件大小）
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'PySide6',
        '--exclude-module', 'wx',
        '--exclude-module', 'pygame',
        '--exclude-module', 'PIL',
        '--exclude-module', 'cv2',
        '--exclude-module', 'sklearn',
        '--exclude-module', 'tensorflow',
        '--exclude-module', 'torch',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'notebook',
        '--exclude-module', 'IPython',
        
        # 性能优化
        '--noconfirm',                       # 不询问覆盖
        '--log-level', 'WARN',               # 只显示警告和错误
        
        # 主程序文件
        'azure_redis_manager.py'
    ]
    
    try:
        # 执行打包命令
        print("执行PyInstaller命令...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ PyInstaller执行成功!")
            return True
        else:
            print("❌ PyInstaller执行失败!")
            print("标准输出:")
            print(result.stdout)
            print("\n错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 打包过程出错: {e}")
        return False

def verify_and_optimize():
    """验证并尝试进一步优化文件"""
    exe_path = Path('dist/AzureRedisManager.exe')
    
    if not exe_path.exists():
        print("\n❌ 可执行文件未生成")
        return False
    
    file_size = exe_path.stat().st_size
    if file_size == 0:
        print("\n❌ 生成的文件大小为0，打包失败")
        return False
    
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n✅ 单文件生成成功!")
    print(f"📁 文件位置: {exe_path.absolute()}")
    print(f"📊 文件大小: {file_size_mb:.1f} MB")
    
    # 尝试UPX压缩（如果可用）
    try:
        print("\n🗜️  尝试UPX压缩...")
        upx_result = subprocess.run(['upx', '--best', str(exe_path)], 
                                  capture_output=True, text=True)
        if upx_result.returncode == 0:
            new_size = exe_path.stat().st_size / (1024 * 1024)
            compression_ratio = (1 - new_size / file_size_mb) * 100
            print(f"✅ UPX压缩成功! 新大小: {new_size:.1f} MB (减小 {compression_ratio:.1f}%)")
        else:
            print("ℹ️  UPX不可用或压缩失败，使用原始文件")
    except FileNotFoundError:
        print("ℹ️  UPX未安装，跳过压缩")
    
    return True

def test_executable():
    """测试可执行文件"""
    exe_path = Path('dist/AzureRedisManager.exe')
    
    print(f"\n🧪 测试可执行文件...")
    
    # 检查文件是否可执行
    if not exe_path.exists():
        print("❌ 文件不存在")
        return False
    
    if exe_path.stat().st_size == 0:
        print("❌ 文件大小为0")
        return False
    
    print("✅ 文件检查通过")
    
    # 询问是否启动测试
    while True:
        choice = input("🚀 是否启动程序进行功能测试? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            try:
                print("正在启动程序...")
                subprocess.Popen([str(exe_path)])
                print("✅ 程序已启动，请在GUI中测试功能")
                return True
            except Exception as e:
                print(f"❌ 启动失败: {e}")
                return False
        elif choice in ['n', 'no', '否']:
            print("ℹ️  跳过功能测试")
            return True
        else:
            print("请输入 y 或 n")

def main():
    """主函数"""
    print_banner()
    
    # 检查主程序文件
    if not os.path.exists("azure_redis_manager.py"):
        print("❌ 错误: 找不到 azure_redis_manager.py")
        input("按Enter键退出...")
        return 1
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller已就绪")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                         check=True, capture_output=True)
            print("✅ PyInstaller安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller安装失败: {e}")
            input("按Enter键退出...")
            return 1
    
    # 清理构建文件
    clean_build_files()
    
    # 构建单文件
    if not build_single_file():
        print("\n❌ 单文件构建失败")
        input("按Enter键退出...")
        return 1
    
    # 验证和优化
    if not verify_and_optimize():
        print("\n❌ 文件验证失败")
        input("按Enter键退出...")
        return 1
    
    # 测试可执行文件
    test_executable()
    
    print("\n" + "=" * 55)
    print("🎉 单文件打包完成!")
    print("=" * 55)
    print("\n📋 使用说明:")
    print("1. 将 dist/AzureRedisManager.exe 复制到目标电脑")
    print("2. 双击运行即可，完全独立，无需任何依赖")
    print("3. 输入Azure Redis连接信息开始使用")
    print("\n💡 特点:")
    print("- 单一exe文件，便于分发")
    print("- 完全独立运行")
    print("- 启动速度较快")
    print("- 支持所有Windows版本")
    
    input("\n按Enter键退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
