# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['azure_redis_manager.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.simpledialog', 'redis', 'redis.connection', 'redis.exceptions', 'threading', 'queue', 'socket', 'ssl', 'datetime', 'time', 'json', 'logging'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx', 'pygame', 'PIL', 'cv2', 'sklearn', 'tensorflow', 'torch', 'jupyter', 'notebook', 'IPython'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='AzureRedisManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
