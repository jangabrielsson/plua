#!/usr/bin/env python3
"""
Generate a comprehensive PyInstaller spec file for PLua
"""

spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['plua.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('lua', 'lua'),
        ('extensions', 'extensions'),
        ('examples', 'examples'),
        ('demos', 'demos'),
        ('pyproject.toml', '.'),
    ],
    hiddenimports=[
        'lupa',
        'lupa.lua',
        'lupa._lupa',
        'toml',
        'toml.decoder',
        'toml.encoder',
        'toml.parser',
        'toml.types',
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
        'extensions.web_server',
        'extensions.websocket_extensions',
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
'''

with open('plua.spec', 'w') as f:
    f.write(spec_content)

print("Generated plua.spec file") 