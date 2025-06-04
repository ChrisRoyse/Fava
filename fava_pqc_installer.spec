# PyInstaller spec file for Fava with PQC Integration

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, copy_metadata, collect_data_files
# try:
#     import oqs
#     oqs_package_dir = os.path.dirname(oqs.__file__)
#     # Adjust 'liboqs.dll' if the actual filename is different on Windows
#     liboqs_dll_path_old = os.path.join(oqs_package_dir, 'liboqs.dll')
#     if not os.path.exists(liboqs_dll_path_old):
#         print(f"WARNING: liboqs.dll not found at {liboqs_dll_path_old}", file=sys.stderr)
#         liboqs_dll_path_old = None
# except ImportError:
#     print("WARNING: oqs module not found. Cannot locate liboqs.dll.", file=sys.stderr)
#     liboqs_dll_path_old = None

# Manually specify the path to the built oqs.dll
# IMPORTANT: Ensure this path uses forward slashes or os.path.join for cross-platform compatibility within the spec file.
# The actual path on the system is c:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll
liboqs_dll_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
print(f"INFO: Attempting to use DLL from: {liboqs_dll_path}", file=sys.stderr)
if not os.path.exists(liboqs_dll_path):
    print(f"CRITICAL WARNING: DLL not found at manually specified path: {liboqs_dll_path}", file=sys.stderr)
    liboqs_dll_path = None # This will trigger the critical warning below if not found

custom_binaries = []
if liboqs_dll_path:
    # The tuple is (source_path, destination_in_bundle)
    # We want the built 'oqs.dll' (pointed to by liboqs_dll_path)
    # to be named 'liboqs.dll' in the bundle's root.
    custom_binaries.append((liboqs_dll_path, '.'))
    print(f"INFO: Will attempt to bundle '{liboqs_dll_path}' as 'oqs.dll' in the bundle root directory", file=sys.stderr)
else:
    print("CRITICAL WARNING: liboqs_dll_path is None (likely DLL not found at specified path). It will NOT be bundled.", file=sys.stderr)

# --- Fava Application Specifics ---
# Identify the main script for Fava. This is often cli.py or __main__.py.
# Assuming src/fava/cli.py is the entry point.
FAVA_MAIN_SCRIPT = 'src/fava/cli.py'

# --- Data Files ---
# This section needs to be carefully curated.
# It should include:
# 1. Fava's own static assets (templates, base static files).
# 2. Built frontend assets (JS, CSS, WASM modules, images, fonts from the frontend/ build).
#    The path to these built assets needs to be determined (e.g., 'src/fava/static/dist/').
# 3. PQC related files if not automatically picked up (e.g., specific .dlls if oqs-python hooks are insufficient).

fava_datas = [
    # Fava's core templates and static files
    ('src/fava/templates', 'fava/templates'),
    # src/fava/static/ includes base static files (e.g., favicon) AND
    # built frontend assets (app.js, .wasm, .woff2) output by frontend/build.ts
    ('src/fava/static', 'fava/static'),
    ('src/fava/help', 'fava/help'),     # Help files
    # PQC WASM modules, if handled by esbuild's "file" loader, will be in src/fava/static/
    # and included by the above line. If they are located elsewhere or need special handling,
    # they might need a separate entry.
]

# --- oqs-python and C Dependencies ---
# PyInstaller might need help finding oqs-python's C dependencies (liboqs.dll).
# A hook file (e.g., hook-oqs.py) might be necessary.
# Alternatively, explicitly add the .dlls to `binaries`.
# The exact path to liboqs.dll within the oqs-python installation or a pre-built SDK needs to be known.
# Example (adjust path and DLL name as needed):
# oqs_binaries = [
#    ('/path/to/liboqs.dll', '.'), # Bundles liboqs.dll into the root of the exe's temp dir
# ]
# Or, rely on a hook. For now, we'll assume a hook might be needed or PyInstaller handles it.
oqs_binaries = []


# --- Collect Metadata and Data files ---
all_metadata = []
all_metadata.extend(copy_metadata('fava'))
all_metadata.extend(copy_metadata('lml'))
all_metadata.extend(copy_metadata('pyexcel'))
all_metadata.extend(copy_metadata('pyexcel_io'))
all_metadata.extend(copy_metadata('pyexcel_xls'))
all_metadata.extend(copy_metadata('pyexcel_xlsx'))
all_metadata.extend(copy_metadata('pyexcel_ods3'))
all_metadata.extend(copy_metadata('pyexcel_text'))
all_metadata.extend(copy_metadata('beancount'))    # Added based on debug_incorrect_bundle_structure_report_v10.md
# Add any other packages for which metadata is essential

# Fava's core data files (renamed from fava_datas for clarity with report example)
current_fava_datas = [
    ('src/fava/templates', 'fava/templates'),
    ('src/fava/static', 'fava/static'),
    ('src/fava/help', 'fava/help'),
]

# Collect other specific data files that are not metadata
# Based on report example, though specific needs might vary.
# Assuming these are beneficial as per the diagnostic report's thoroughness.
pyexcel_specific_data = collect_data_files('pyexcel', include_py_files=False)
pyexcel_io_specific_data = collect_data_files('pyexcel_io', include_py_files=False)

datas_for_analysis = current_fava_datas + all_metadata + pyexcel_specific_data + pyexcel_io_specific_data + [('.venv/Lib/site-packages/beancount/VERSION', 'beancount')]

# --- Analysis ---
# pathex: Paths to search for imports. Add 'src' to find the fava package.
a = Analysis(
    [FAVA_MAIN_SCRIPT],
    pathex=['src'], # Ensure 'fava' module can be found
    binaries=custom_binaries,
    datas=datas_for_analysis, # MODIFIED HERE
    hiddenimports=[
        # Fava specific (already present, kept for reference, ensure they are still needed)
        'babel.numbers',
        'jinja2',
        'werkzeug',
        'fava.beans.abc',
        'fava.core',
        'fava.core.accounts',
        'fava.core.attributes',
        'fava.core.budgets',
        'fava.core.charts',
        'fava.core.commodities',
        'fava.core.conversion',
        'fava.core.documents',
        'fava.core.extensions',
        'fava.core.fava_options',
        'fava.core.file',
        'fava.core.filters',
        'fava.core.group_entries',
        'fava.core.ingest',
        'fava.core.inventory',
        'fava.core.misc',
        'fava.core.module_base',
        'fava.core.number',
        'fava.core.query_shell',
        'fava.core.watcher',
        'fava.core.tree',
        'fava.ext',
        'fava.ext.auto_commit',
        'fava.ext.portfolio_list',
        'fava.plugins',
        'fava.plugins.link_documents',
        'fava.plugins.tag_discovered_documents',
        'fava.pqc',
        'fava.pqc.app_startup',
        'fava.pqc.backend_crypto_service',
        'fava.pqc.configuration_validator',
        'fava.pqc.crypto_lib_helpers',
        'fava.pqc.documentation_generator',
        'fava.pqc.exceptions',
        'fava.pqc.frontend_crypto_facade',
        'fava.pqc.frontend_lib_helpers',
        'fava.pqc.global_config',
        'fava.pqc.global_config_helpers',
        'fava.pqc.gpg_handler',
        'fava.pqc.hashers',
        'fava.pqc.interfaces',
        'fava.pqc.proxy_awareness',
        'oqs',
        'tzdata',

        # pyexcel related hidden imports are now largely handled by hooks in the 'hooks/' directory.
        # Retaining fava, oqs, and other general dependencies.
    ],
    hookspath=['hooks/'], # Path to custom hook files for pyexcel, lml, etc.
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# --- PYZ (Python Archive) ---
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- EXE ---
exe = EXE(
    pyz,
    a.scripts,
    [], # binaries to be added to EXE directly (usually empty)
    exclude_binaries=True, # binaries are collected in 'collect' step
    name='fava_pqc_installer', # Output .exe name (without version for now)
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # UPX compression disabled for diagnosing oqs.dll issue
    console=True, # Fava is a CLI that launches a web server, so console might be useful for logs
    disable_windowed_traceback=False,
    target_arch=None, # Autodetect, or 'x86_64' for 64-bit
    codesign_identity=None,
    entitlements_file=None,
    icon='src/fava/static/favicon.ico' # Path to Fava's icon
)

# --- COLLECT (Bundle everything into a single directory or one-file) ---
# For one-file bundle:
coll = COLLECT(
    exe,
    a.binaries, # Collect all binaries (Python's own, oqs-python's .dlls, etc.)
    a.zipfiles, # Usually empty
    a.datas,    # Collect all data files
    strip=False,
    upx=False, # UPX compression disabled for diagnosing oqs.dll issue
    upx_exclude=[],
    name='fava_pqc_dist' # Name of the folder if not onefile, or temp folder for onefile
)

# Note: To make this a true single .exe installer, this .spec file would typically be used
# by PyInstaller to create a bundled Fava application (e.g., fava_pqc_app.exe).
# Then, an installer tool like Inno Setup or NSIS would take this output
# (the fava_pqc_dist folder or the single fava_pqc_app.exe) and create the
# final `fava_pqc_installer_vX.Y.Z.exe`.
# This spec file focuses on bundling the Fava application itself.
# The "name" in EXE will be the bundled app's name.
# The final installer's name is usually set by the installer tool (Inno Setup, NSIS).