# PyInstaller hook for the 'pyexcel-ods3' library.
#
# 'pyexcel-ods3' is a plugin for 'pyexcel' providing ODS (OpenDocument Spreadsheet)
# file format support (specifically for ODS v1.2 and above via odfpy).
# This hook ensures its metadata (for plugin discovery), data files,
# and submodules are included in the bundle.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel-ods3
datas = copy_metadata('pyexcel_ods3')

# Collect any data files associated with pyexcel-ods3
datas += collect_data_files('pyexcel_ods3')

# Collect all submodules of pyexcel-ods3
hiddenimports = collect_submodules('pyexcel_ods3')