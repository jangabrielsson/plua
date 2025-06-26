# PyInstaller hook for lupa
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('lupa')

# Collect any data files
datas = collect_data_files('lupa')

# Explicitly include the C extension
binaries = [] 