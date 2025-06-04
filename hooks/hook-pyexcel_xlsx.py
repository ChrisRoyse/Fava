# PyInstaller hook for the 'pyexcel-xlsx' library.
#
# 'pyexcel-xlsx' is a plugin for 'pyexcel' providing XLSX file format support.
# This hook ensures its metadata (for plugin discovery by 'lml' via 'pyexcel'),
# its data files, and its submodules are included in the bundle.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel-xlsx
datas = copy_metadata('pyexcel_xlsx')

# Collect any data files associated with pyexcel-xlsx
datas += collect_data_files('pyexcel_xlsx')

# Collect all submodules of pyexcel-xlsx
hiddenimports = collect_submodules('pyexcel_xlsx')