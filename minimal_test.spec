# minimal_test.spec
import os
block_cipher = None
# Ensure this path is correct relative to where PyInstaller runs the spec
dll_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
print(f"MINIMAL_TEST_SPEC: Attempting to bundle DLL: {dll_path}")
print(f"MINIMAL_TEST_SPEC: DLL Exists: {os.path.exists(dll_path)}")
a = Analysis(['minimal_script.py'],
             pathex=[],
             binaries=[(dll_path, '.')],
             datas=[],
             hiddenimports=['oqs'], # Added oqs to hiddenimports
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts,[], exclude_binaries=True, name='minimal_test_app', console=True, debug=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='minimal_test_output')