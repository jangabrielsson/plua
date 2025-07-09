# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('src/lua', 'lua'), ('src/extensions', 'extensions'), ('pyproject.toml', '.')]
binaries = []
hiddenimports = ['lupa', 'lupa._lupa', 'lupa.lua', 'lupa.lua_types', 'asyncio', 'threading', 'socket', 'urllib.request', 'urllib.parse', 'urllib.error', 'ssl', 'json', 'time', 'os', 'sys', 'argparse', 'queue']
hiddenimports += collect_submodules('lupa')
hiddenimports += collect_submodules('plua')
hiddenimports += collect_submodules('extensions')
tmp_ret = collect_all('lupa')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src/plua/__main__.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
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
