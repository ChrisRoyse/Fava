# PyInstaller hook for the 'pyexcel' library.
#
# 'pyexcel' uses a plugin architecture, often managed by 'lml'.
# This hook ensures that 'pyexcel' itself, its metadata (for potential
# direct plugin registration or other metadata uses), its data files,
# and its submodules (especially 'pyexcel.plugins') are included.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel
# datas = copy_metadata('pyexcel') # Metadata collection moved to .spec file

# Collect any data files associated with pyexcel
# datas += collect_data_files('pyexcel') # Data file collection moved to .spec file

# Collect all submodules of pyexcel, including 'pyexcel.plugins'
# which is crucial for its plugin system.
hiddenimports = collect_submodules('pyexcel')
datas = [] # Ensure datas is defined if other logic in this hook were to use it.
           # Or remove if not used elsewhere in this hook.
           # For now, keeping it as an empty list as a safe default.