# PyInstaller hook for the 'pyexcel-text' library.
#
# 'pyexcel-text' is a plugin for 'pyexcel' providing support for
# text-based spreadsheet formats like CSV, TSV.
# This hook ensures its metadata (for plugin discovery), data files,
# and submodules are included in the bundle.
# This is important for resolving issues like missing 'pyexcel_io.readers.csv_in_file'.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel-text
datas = copy_metadata('pyexcel_text')

# Collect any data files associated with pyexcel-text
datas += collect_data_files('pyexcel_text')

# Collect all submodules of pyexcel-text
hiddenimports = collect_submodules('pyexcel_text')