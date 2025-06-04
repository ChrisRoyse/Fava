import oqs
import os

# Attempt to print the path of the loaded liboqs library
try:
    if hasattr(oqs, '_liboqs') and oqs._liboqs is not None and hasattr(oqs._liboqs, '_name'):
        print(f"DEBUG: oqs._liboqs._name (path to loaded DLL) = {oqs._liboqs._name}")
        # Additionally, check if this path actually exists
        if oqs._liboqs._name and os.path.exists(oqs._liboqs._name):
            print(f"DEBUG: The path oqs._liboqs._name exists: {oqs._liboqs._name}")
        elif oqs._liboqs._name:
            print(f"DEBUG: The path oqs._liboqs._name DOES NOT exist: {oqs._liboqs._name}")
        else:
            print(f"DEBUG: oqs._liboqs._name is None or empty.")

    else:
        print("DEBUG: oqs._liboqs or oqs._liboqs._name not accessible.")
except Exception as e_debug:
    print(f"DEBUG: Error trying to access oqs._liboqs._name: {e_debug}")

# Original test for get_lib_path (expected to fail)
try:
    lib_path = oqs.get_lib_path() # This will raise AttributeError
    print(f"oqs.get_lib_path() returned: {lib_path}")
    if lib_path and os.path.exists(lib_path):
        print(f"SUCCESS: oqs.dll found at {lib_path}")
    else:
        print(f"FAILURE: oqs.dll NOT found at path returned by get_lib_path() or path is invalid (returned: {lib_path}).")
except AttributeError as ae:
    if 'get_lib_path' in str(ae):
        print("FAILURE: oqs.get_lib_path() is not available. oqs-python might be misconfigured or too old.")
    else:
        print(f"FAILURE: An AttributeError occurred during get_lib_path test: {ae}")
except Exception as e:
    print(f"FAILURE: An error occurred during get_lib_path test: {e}")