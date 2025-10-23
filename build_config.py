# -*- mode: python ; coding: utf-8 -*-

# Azure Redis Manager 打包配置
# 用于 PyInstaller 创建可执行文件

import os
import sys

# 应用程序信息
APP_NAME = "Azure Redis Manager"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Azure Redis 数据库管理工具"
APP_AUTHOR = "AzureRedisTool"

# 打包配置
MAIN_SCRIPT = "azure_redis_manager.py"
ICON_FILE = None  # 如果有图标文件可以指定路径

# PyInstaller 配置
block_cipher = None

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'redis',
        'threading',
        'queue',
        'socket',
        'ssl',
        'datetime',
        'time',
        'json'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AzureRedisManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE,
    version_info={
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
        'company': APP_AUTHOR,
        'product': APP_NAME,
        'copyright': f'Copyright (c) 2024 {APP_AUTHOR}',
        'file_version': APP_VERSION,
        'product_version': APP_VERSION,
    }
)
