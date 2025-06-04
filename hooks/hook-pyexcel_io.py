# PyInstaller hook for the 'pyexcel-io' library.
#
# 'pyexcel-io' is a core I/O handling component for 'pyexcel'.
# It manages various readers and writers, often as plugins.
# This hook ensures its metadata, data files, and all submodules
# (like 'pyexcel_io.plugins', 'pyexcel_io.readers', 'pyexcel_io.writers')
# are correctly bundled.

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Include metadata for pyexcel-io
datas = copy_metadata('pyexcel_io')

# Collect any data files associated with pyexcel-io
datas += collect_data_files('pyexcel_io')

# Collect all submodules of pyexcel-io. This is critical for
# including all its internal plugins, readers, and writers.
hiddenimports = collect_submodules('pyexcel_io')