# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/plua/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/lua', 'lua'),
        ('src/extensions', 'extensions'),
        ('examples', 'examples'),
    ],
    hiddenimports=[
        'lupa',
        'asyncio',
        'socket',
        'threading',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'ssl',
        'paho.mqtt.client',
        'extensions.network_extensions',
        'extensions.html_extensions',
        'extensions.core',
        'extensions.registry',
        'plua',
        'plua.interpreter',
        'plua.embedded_api_server',
        'plua.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='plua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
