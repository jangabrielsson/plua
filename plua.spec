# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('src/lua', 'lua'), ('src/extensions', 'extensions'), ('pyproject.toml', '.')]
binaries = []
hiddenimports = ['lupa', 'lupa._lupa', 'lupa.lua', 'lupa.lua_types', 'asyncio', 'threading', 'socket', 'urllib.request', 'urllib.parse', 'urllib.error', 'ssl', 'json', 'time', 'os', 'sys', 'argparse', 'queue', 'requests']
hiddenimports += collect_submodules('lupa')
hiddenimports += collect_submodules('plua')
hiddenimports += collect_submodules('extensions')
tmp_ret = collect_all('lupa')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Exclude unnecessary modules for faster startup
excludes = [
    'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'Pillow', 'tkinter', 'wx',
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'IPython', 'jupyter', 'notebook',
    'pytest', 'pytest_*', 'unittest', 'doctest', 'test', 'tests',
    'setuptools', 'distutils', 'wheel', 'pip', 'pkg_resources',
    'email', 'html', 'xml', 'xmlrpc', 'ftplib', 'telnetlib',
    'multiprocessing', 'concurrent.futures',
    'sqlite3', 'dbm', 'shelve',
    'calendar', 'locale', 'gettext',
    'pydoc', 'doctest', 'unittest', 'test', 'lib2to3',
    'pkg_resources', 'setuptools', 'distutils', 'wheel',
    'pip', 'ensurepip', 'venv', 'virtualenv',
    'pdb', 'bdb', 'faulthandler',
    'warnings', 'weakref', 'abc', 'collections.abc',
    'typing', 'typing_extensions', 'dataclasses',
    'functools', 'itertools', 'operator',
    'contextlib', 'contextvars', 'copy', 'copyreg',
    'gc', 'inspect', 'linecache',
    'pickle', 'pickletools', 'pkgutil', 'platform',
    'posixpath', 'site', 'sre_compile', 'sre_constants',
    'sre_parse', 'stat', 'string', 'struct', 'sysconfig',
    'token', 'tokenize', 'traceback', 'types', 'warnings',
    'weakref', 'zipimport', 'zlib',
]

a = Analysis(
    ['src/plua/__main__.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,  # Disable optimization to avoid compatibility issues
)
pyz = PYZ(a.pure, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='plua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols for smaller size
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
