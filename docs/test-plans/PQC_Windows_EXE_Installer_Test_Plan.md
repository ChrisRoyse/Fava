# Test Plan: PQC Windows EXE Installer for Fava

## 1. Introduction

This document outlines the granular test plan for the Fava Windows `.exe` installer with PQC integration. It is based on the requirements and acceptance criteria defined in [`docs/specifications/PQC_Windows_EXE_Installer_Spec.md`](docs/specifications/PQC_Windows_EXE_Installer_Spec.md). This plan focuses on verifying the installer's build process, installation, functionality of the installed application (including PQC features), and uninstallation.

## 2. Scope of Testing

-   Installer build process.
-   Installation on target Windows systems.
-   Core Fava application functionality post-installation.
-   PQC feature functionality post-installation.
-   Dependency integrity (Python modules, C extensions, DLLs, frontend assets).
-   Uninstallation process.

## 3. Test Environment

-   **Operating System:** Windows 10 (64-bit) and Windows 11 (64-bit). Clean virtual machines are preferred for each test cycle to ensure no interference from previous installations.
-   **Build Environment:** As defined by the selected packaging tool (e.g., Python environment with PyInstaller, cx_Freeze, or Nuitka installed, along with any necessary build tools like Inno Setup or NSIS).
-   **Test Data:** A set of sample Beancount files, including some that might exercise PQC-specific features if applicable (e.g., files with metadata that could be PQC-hashed or entries that might be PQC-encrypted if Fava supports this directly).

## 4. Test Cases

### 4.1. Installer Build Process (Corresponds to AC1)

| Test Case ID | Description                                      | Steps                                                                                                                              | Expected Results                                                                                                   | Priority |
|--------------|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|----------|
| TP-BUILD-001 | Verify successful installer build                | 1. Set up the build environment. <br> 2. Execute the installer build script/command.                                                  | 1. Build process completes without errors. <br> 2. A single `.exe` installer file is generated in the `dist/` directory. | High     |
| TP-BUILD-002 | Verify all components are included in the build  | 1. Inspect the build logs or use tool-specific methods to verify inclusion of: Fava, Python deps, `oqs-python`, `liboqs.dll`, frontend assets. | 1. Logs confirm inclusion or manual inspection of intermediate build artifacts shows all components are present.   | High     |

### 4.2. Installation Process (Corresponds to AC2)

| Test Case ID | Description                                          | Steps                                                                                                                                                                                             | Expected Results                                                                                                                                                                                            | Priority |
|--------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| TP-INSTALL-001 | Verify successful installation with default path   | 1. On a clean Windows 10/11 VM, run the installer `.exe`. <br> 2. Accept license (if any). <br> 3. Accept default installation path. <br> 4. Complete installation.                                       | 1. Installation completes without errors. <br> 2. Fava is installed to the default path. <br> 3. Start Menu shortcut is created. <br> 4. Desktop shortcut is created (if selected).                               | High     |
| TP-INSTALL-002 | Verify successful installation with custom path    | 1. On a clean Windows 10/11 VM, run the installer `.exe`. <br> 2. Accept license. <br> 3. Choose a custom installation path (e.g., `D:\FavaPQC`). <br> 4. Complete installation.                             | 1. Installation completes without errors. <br> 2. Fava is installed to the custom path. <br> 3. Shortcuts are created.                                                                                     | Medium   |
| TP-INSTALL-003 | Verify installation with non-admin rights (if supported for user path) | 1. On a clean Windows 10/11 VM, logged in as a non-admin user, run installer. <br> 2. Choose user-specific path (e.g. AppData\Local\Programs). <br> 3. Complete. | 1. Installation completes without admin prompt (if path allows). <br> 2. Fava installed. <br> 3. Shortcuts created. | Medium   |
| TP-INSTALL-004 | Verify installation requiring admin rights (Program Files) | 1. On a clean Windows 10/11 VM, run installer. <br> 2. Choose `C:\Program Files\FavaPQC`. <br> 3. Complete. | 1. Admin rights prompted and granted. <br> 2. Installation completes. <br> 3. Fava installed. <br> 4. Shortcuts created. | Medium   |

### 4.3. Application Launch & Core Functionality (Corresponds to AC3)

| Test Case ID | Description                               | Steps                                                                                                                               | Expected Results                                                                                                                               | Priority |
|--------------|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| TP-APP-001   | Verify application launch from Start Menu | 1. After installation, open Fava from the Start Menu shortcut.                                                                      | 1. Fava application launches successfully. <br> 2. Main UI is displayed correctly (e.g., browser opens to Fava page if it's a web application). | High     |
| TP-APP-002   | Verify application launch from executable | 1. Navigate to the installation directory. <br> 2. Run the main Fava executable directly.                                           | 1. Fava application launches successfully. <br> 2. Main UI is displayed correctly.                                                            | Medium   |
| TP-APP-003   | Verify loading Beancount file             | 1. Launch Fava. <br> 2. Load a sample Beancount file.                                                                               | 1. Beancount file loads without errors. <br> 2. Account data is displayed.                                                                   | High     |
| TP-APP-004   | Verify core report generation             | 1. With a Beancount file loaded, navigate to: Balance Sheet, Income Statement, Journal.                                            | 1. Reports are generated and displayed correctly without errors.                                                                               | High     |

### 4.4. PQC Feature Functionality (Corresponds to AC4)

| Test Case ID | Description                                       | Steps                                                                                                                                                           | Expected Results                                                                                                                                                              | Priority |
|--------------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| TP-PQC-001   | Verify PQC algorithm availability (if applicable) | 1. Launch Fava. <br> 2. Navigate to any settings or operations where PQC algorithms can be selected/configured.                                                 | 1. Configured PQC algorithms are listed/available.                                                                                                                              | High     |
| TP-PQC-002   | Verify PQC hashing (if applicable)                | 1. Perform an action in Fava that utilizes PQC hashing (e.g., generating a hash for a transaction or document if this feature exists).                             | 1. Hashing operation completes successfully using the configured PQC algorithm. <br> 2. The generated hash is consistent/correct (if a known value can be pre-calculated). | High     |
| TP-PQC-003   | Verify PQC data at rest (if applicable)           | 1. Perform an action that encrypts data using PQC (e.g., encrypting a Beancount file or specific entries). <br> 2. Perform an action that decrypts the PQC-encrypted data. | 1. Encryption and decryption operations complete successfully. <br> 2. Data integrity is maintained.                                                                       | High     |
| TP-PQC-004   | Verify PQC WASM module integrity (frontend)       | 1. Launch Fava and open browser developer tools. <br> 2. Monitor console for WASM loading and integrity check messages. <br> 3. Interact with UI elements relying on PQC WASM. | 1. WASM modules for PQC load successfully. <br> 2. Integrity checks pass (if logged). <br> 3. UI elements function correctly.                                                  | High     |

### 4.5. Dependency Integrity (Corresponds to AC5)

| Test Case ID | Description                                  | Steps                                                                                                                                  | Expected Results                                                                                                  | Priority |
|--------------|----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|----------|
| TP-DEP-001   | Verify no missing Python modules             | 1. Launch Fava. <br> 2. Navigate through various features and reports.                                                                  | 1. No `ModuleNotFoundError` or similar Python import errors occur.                                                  | High     |
| TP-DEP-002   | Verify `oqs-python` C extension functionality | 1. Perform an operation that explicitly uses `oqs-python` (e.g., a PQC cryptographic operation).                                         | 1. The operation completes successfully. <br> 2. No errors related to loading `oqs-python` or its C dependencies. | High     |
| TP-DEP-003   | Verify `liboqs.dll` (or equivalent) loading  | 1. Monitor application behavior and logs (if any) during PQC operations. Use tools like Process Monitor if necessary to check DLL loads. | 1. `liboqs.dll` (or its equivalent for the bundled PQC library) is loaded successfully by the Fava process.       | High     |
| TP-DEP-004   | Verify frontend asset loading                | 1. Launch Fava. <br> 2. Open browser developer tools (Network tab). <br> 3. Verify all JS, CSS, images, and WASM files load with HTTP 200. | 1. All frontend assets load correctly without 404 errors.                                                       | High     |

### 4.6. Uninstallation Process (Corresponds to AC6)

| Test Case ID | Description                                  | Steps                                                                                                                                                              | Expected Results                                                                                                                                                                                             | Priority |
|--------------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| TP-UNINSTALL-001 | Verify successful uninstallation           | 1. After installation, go to Windows "Add or remove programs". <br> 2. Select Fava and choose "Uninstall". <br> 3. Follow uninstallation prompts.                   | 1. Uninstallation completes without errors. <br> 2. Fava application files and directories (from install path) are removed. <br> 3. Start Menu and Desktop shortcuts are removed.                               | High     |
| TP-UNINSTALL-002 | Verify user data is not deleted            | 1. Before uninstallation, create/place a sample Beancount file or Fava configuration file in a user directory (e.g., Documents). <br> 2. Uninstall Fava.           | 1. The user-generated Beancount file and Fava configuration (if stored outside install dir) remain untouched.                                                                                                | High     |

## 5. Test Execution and Reporting
-   Each test case will be executed manually.
-   Results (Pass/Fail), along with any observations, errors, or logs, will be recorded.
-   A final test summary report will be generated, detailing overall pass/fail rates and any outstanding issues.