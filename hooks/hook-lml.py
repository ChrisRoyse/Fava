# PyInstaller hook for the 'lml' library.
#
# The 'lml' library is used by 'pyexcel' for its plugin system.
# It relies on package metadata (entry points) to discover plugins.
# 'copy_metadata' ensures this metadata is included in the bundle.
# 'collect_submodules' ensures all of lml's own modules are included.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules

# Include metadata for lml, crucial for plugin discovery via entry_points
# datas = copy_metadata('lml') # Metadata collection moved to .spec file

# Include all submodules of lml
hiddenimports = collect_submodules('lml')
datas = [] # Ensure datas is defined if other logic in this hook were to use it.
           # Or remove if not used elsewhere in this hook.
           # For now, keeping it as an empty list as a safe default.