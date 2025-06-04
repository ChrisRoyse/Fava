# Research: Windows .exe Installer for Python Applications

When creating Windows `.exe` installers for Python applications with C extensions and frontend assets (JavaScript/CSS), tool selection and configuration critically depend on performance, dependency handling, and deployment requirements. Below is an analysis of **PyInstaller**, **cx_Freeze**, and **Nuitka**, along with best practices for handling complex dependencies like `oqs-python`.

---

## Tool Comparison

| **Feature**               | **PyInstaller**                                  | **cx_Freeze**                                  | **Nuitka**                                     |
|---------------------------|--------------------------------------------------|------------------------------------------------|------------------------------------------------|
| **Compilation Method**    | Bundles Python interpreter and dependencies     | Freezes code into `.pyc` files                 | Compiles Python to optimized C/C++            |
| **Single-File Exe**       | Yes                                              | No                                             | Yes                                            |
| **Dependency Handling**   | Automatic via hooks; manual overrides available | Auto-includes imports; manual `setup.py` config| Requires explicit plugin support for binaries  |
| **C Extensions**          | Supported via hooks or manual spec files        | Supported with proper configuration           | Native integration via C compilation           |
| **Frontend Assets**       | Added via `--add-data` or spec files            | Included via `include_files` in `setup.py`     | Manual inclusion via `--include-data-files`    |
| **Code Obfuscation**      | Limited (bytecode-only)                          | Limited (bytecode-only)                        | High (C compilation)                           |
| **Performance**           | Standard Python runtime                          | Standard Python runtime                        | Optimized native binaries                      |
| **Cross-Compilation**     | No                                               | No                                             | No                                             |

---

### PyInstaller
**Strengths**:
- **Mature ecosystem** with extensive documentation and community support.
- **Single-file executables** simplify distribution.
- Handles **C extensions** via hooks (e.g., `hook-oqs.py` to include `oqs-python` binaries).

**Example Configuration**:
```python
# spec file to include C extensions and frontend assets
a = Analysis(
    ['app.py'],
    datas=[('static/*.js', 'static'), ('static/*.css', 'static')],
    hooks=['hooks/hook-oqs.py'],
    # ...
)
```

**Limitations**:
- Large output size due to bundling the full Python interpreter.
- Manual hook setup required for non-standard dependencies.

---

### cx_Freeze
**Strengths**:
- **Simpler configuration** using `setup.py` for basic projects.
- Automatically includes imported modules (reduces manual dependency tracking).

**Example Configuration**:
```python
# setup.py for cx_Freeze
from cx_Freeze import setup, Executable

build_options = {
    "packages": ["oqs"],
    "include_files": ["static/", "config.ini"],
}

setup(
    executables=[Executable("app.py")],
    options={"build_exe": build_options},
)
```

**Limitations**:
- No single-file executable support.
- Less effective for obfuscation (`.pyc` files are reversible).

---

### Nuitka
**Strengths**:
- **Native performance** via C compilation.
- Built-in **code obfuscation** (harder to decompile than `.pyc`).
- Efficient handling of C extensions (compiles them directly).

**Example Command**:
```bash
nuitka --windows-disable-console --onefile --include-data-dir=static=static --enable-plugin=oqs app.py
```

**Limitations**:
- Steeper learning curve for complex projects.
- Limited plugin support for some third-party libraries.

---

## Best Practices
1. **Dependency Management**:
   - Use `virtualenv` to isolate project dependencies.
   - For `oqs-python`, ensure shared libraries (e.g., `.dll` files) are included via tool-specific methods:
     - PyInstaller: Add to `datas` in spec files.
     - Nuitka: Use `--include-data-files=/path/to/oqs.dll=.`.

2. **Frontend Assets**:
   - Bundle JS/CSS via:
     - PyInstaller: `--add-data "static:static"`.
     - cx_Freeze: `include_files=["static/"]`.
     - Nuitka: `--include-data-dir=static=static`.

3. **Installer Creation**:
   - Pair tools like **Inno Setup** or **NSIS** with the generated executables to create professional installers.
   - For code signing, use `signtool` (Windows) or `codesign` (macOS).

4. **Testing**:
   - Validate executables on clean Windows VMs to catch missing dependencies.
   - Profile performance for C-heavy applications (Nuitka may offer speed advantages).

---

## Recommendation
- **For simplicity**: PyInstaller is ideal for quick builds with moderate asset complexity.
- **For performance/obfuscation**: Nuitka suits high-stakes applications needing optimized binaries.
- **For basic projects**: cx_Freeze provides a lightweight option but lacks advanced features.

Always combine these tools with post-build installers (e.g., Inno Setup) to manage file associations, registry entries, and system-level integrations.