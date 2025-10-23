#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Redis Manager 打包脚本
使用PyInstaller将Python程序打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 50)
    print("    Azure Redis Manager 打包工具")
    print("=" * 50)
    print()

def check_dependencies():
    """检查必要的依赖"""
    print("正在检查依赖...")
    
    # 检查主程序文件
    if not os.path.exists("azure_redis_manager.py"):
        print("❌ 错误: 找不到 azure_redis_manager.py")
        return False
    
    # 检查Python包
    required_packages = ['redis', 'tkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安装")
    
    if missing_packages:
        print(f"\n正在安装缺失的包: {', '.join(missing_packages)}")
        try:
            if 'redis' in missing_packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'redis==4.5.4'], 
                             check=True, capture_output=True)
                print("✅ Redis包安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 包安装失败: {e}")
            return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller - 已安装")
    except ImportError:
        print("❌ PyInstaller - 未安装，正在安装...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                         check=True, capture_output=True)
            print("✅ PyInstaller安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller安装失败: {e}")
            return False
    
    return True

def clean_build_files():
    """清理之前的构建文件"""
    print("\n正在清理构建文件...")
    
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

def build_executable():
    """构建可执行文件"""
    print("\n开始打包程序...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # 无控制台窗口
        '--name', 'AzureRedisManager',  # 可执行文件名
        '--distpath', 'dist',           # 输出目录
        '--workpath', 'build',          # 工作目录
        '--specpath', '.',              # spec文件位置
        '--clean',                      # 清理临时文件
        
        # 包含的模块
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'redis',
        '--hidden-import', 'threading',
        '--hidden-import', 'queue',
        '--hidden-import', 'socket',
        '--hidden-import', 'ssl',
        '--hidden-import', 'datetime',
        '--hidden-import', 'time',
        '--hidden-import', 'json',
        
        # 排除的模块（减小文件大小）
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'PySide6',
        
        'azure_redis_manager.py'        # 主程序文件
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功!")
            return True
        else:
            print("❌ 打包失败!")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 打包过程出错: {e}")
        return False

def verify_executable():
    """验证生成的可执行文件"""
    exe_path = Path('dist/AzureRedisManager.exe')
    
    if exe_path.exists():
        file_size = exe_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"\n✅ 可执行文件生成成功!")
        print(f"📁 文件位置: {exe_path.absolute()}")
        print(f"📊 文件大小: {file_size_mb:.1f} MB")
        
        return True
    else:
        print("\n❌ 可执行文件未生成")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请解决上述问题后重试")
        input("按Enter键退出...")
        return 1
    
    # 清理构建文件
    clean_build_files()
    
    # 构建可执行文件
    if not build_executable():
        print("\n❌ 构建失败")
        input("按Enter键退出...")
        return 1
    
    # 验证可执行文件
    if not verify_executable():
        print("\n❌ 验证失败")
        input("按Enter键退出...")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 打包完成!")
    print("=" * 50)
    print("\n📋 使用说明:")
    print("1. 将 dist/AzureRedisManager.exe 复制到目标电脑")
    print("2. 双击运行即可，无需安装任何依赖")
    print("3. 输入Azure Redis连接信息开始使用")
    print("\n💡 提示:")
    print("- 可执行文件约20-30MB")
    print("- 支持Windows 7及以上版本")
    print("- 首次运行可能需要几秒钟启动时间")
    
    # 询问是否测试运行
    while True:
        choice = input("\n🚀 是否现在测试运行程序? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            print("正在启动程序进行测试...")
            try:
                subprocess.Popen(['dist/AzureRedisManager.exe'])
                print("✅ 程序已启动")
            except Exception as e:
                print(f"❌ 启动失败: {e}")
            break
        elif choice in ['n', 'no', '否']:
            break
        else:
            print("请输入 y 或 n")
    
    input("\n按Enter键退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
