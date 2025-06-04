# PyInstaller hook for the 'pyexcel-xls' library.
#
# 'pyexcel-xls' is a plugin for 'pyexcel' providing XLS file format support.
# This hook ensures its metadata (for plugin discovery by 'lml' via 'pyexcel'),
# its data files, and its submodules are included in the bundle.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel-xls
datas = copy_metadata('pyexcel_xls')

# Collect any data files associated with pyexcel-xls
datas += collect_data_files('pyexcel_xls')

# Collect all submodules of pyexcel-xls
hiddenimports = collect_submodules('pyexcel_xls')