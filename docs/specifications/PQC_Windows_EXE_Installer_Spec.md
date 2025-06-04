# Specification: PQC Windows EXE Installer for Fava

## 1. Overview

This document outlines the specifications for a Windows `.exe` installer for the Fava application, including all Post-Quantum Cryptography (PQC) integrations. The goal is to produce a production-quality, fully operational installer that simplifies Fava deployment on Windows systems.

## 2. Requirements

### 2.1. Bundled Components
The installer must bundle the following:
-   The Fava application (latest stable version with PQC integrations).
-   All necessary Python dependencies for Fava, including `oqs-python`.
-   The required Python runtime environment (if the chosen packaging tool necessitates it, e.g., PyInstaller).
-   All PQC C library dependencies required by `oqs-python` (e.g., `liboqs.dll` or equivalent).
-   All Fava frontend assets (JavaScript, CSS, images, fonts, WASM modules for PQC).
-   Any necessary configuration files for Fava to run out-of-the-box with PQC features enabled by default where sensible, or clearly documented if requiring user action.

### 2.2. PQC Dependency Handling
-   PQC C library dependencies must be correctly bundled and accessible to the `oqs-python` library within the installed Fava application.
-   The method of bundling (e.g., static linking if possible, or including DLLs in a way that the Python C extension can find them) must ensure robust operation on target systems.

### 2.3. Target Systems
-   **Operating System:** Windows 10 (64-bit) and newer.
-   **Architecture:** x64 (64-bit).

### 2.4. Installer Characteristics
-   **Format:** Single `.exe` file for ease of distribution.
-   **User Interface:** A standard Windows installer GUI (e.g., provided by Inno Setup or NSIS).
    -   Welcome screen.
    -   License agreement display (if applicable).
    -   Installation path selection (with a sensible default, e.g., `C:\Program Files\FavaPQC` or `C:\Users\[Username]\AppData\Local\Programs\FavaPQC`).
    -   Progress bar.
    -   Completion screen.
-   **File Size:** The installer size should be optimized as much as reasonably possible without sacrificing functionality.
-   **Privileges:** The installer should request administrator privileges if necessary for the chosen installation path (e.g., Program Files). Installation to user-specific paths should not require admin rights.

### 2.5. Installation Process
-   The installation must complete without errors on target systems.
-   The installer should create necessary directory structures.
-   **Shortcuts:**
    -   A Start Menu shortcut for Fava.
    -   An optional desktop shortcut.
-   **Configuration:** The installed Fava application should be configured to locate and use its bundled PQC dependencies and frontend assets correctly.

### 2.6. Uninstallation Process
-   A standard uninstallation method must be available via Windows "Add or remove programs".
-   The uninstaller must remove all application files, directories created by the installer, and Start Menu/desktop shortcuts.
-   User-generated data (e.g., Beancount files, Fava settings if stored outside the install directory) should NOT be removed by the uninstaller.

### 2.7. Post-Installation Functionality ("Fully Operational")
The installed Fava application must be "fully operational," meaning:
-   **Launch:** Fava launches successfully from the created shortcuts or by directly running the installed executable.
-   **Core Fava Features:** All standard Fava features (loading Beancount files, displaying reports, querying, etc.) must function as expected.
-   **PQC Feature Integration:**
    -   PQC algorithms are available and selectable where applicable (e.g., in cryptographic settings if Fava exposes these).
    -   PQC-protected data at rest features (if implemented and applicable to the Fava workflow being packaged) function correctly (e.g., encrypting/decrypting files or specific data fields).
    -   PQC hashing mechanisms function correctly.
    -   PQC WASM module integrity checks (if part of the frontend) operate as intended.
    -   PQC for data in transit (if Fava is configured to use HTTPS with PQC, or if it's running behind a PQC-aware proxy and the installer sets this up) is functional. For this installer, assume Fava runs locally and PQC-TLS is out of scope unless explicitly stated otherwise for a specific build.
-   **Frontend Assets:** All frontend components load and function correctly, including PQC-related UI elements and WASM modules.
-   **No Missing Dependencies:** The application runs without errors related to missing DLLs, Python modules, or other assets.

## 3. Acceptance Criteria

### AC1: Installer Build
-   **Given** the Fava source code with PQC integrations and all dependencies are available.
-   **When** the installer build process is executed.
-   **Then** a single `.exe` installer file is successfully created in the designated output directory (e.g., `dist/`).
-   **And** the build process completes without errors.

### AC2: Installation Success
-   **Given** a target Windows system (Windows 10 64-bit or newer).
-   **When** the generated `.exe` installer is executed.
-   **Then** the Fava application installs successfully to the chosen/default path.
-   **And** Start Menu (and optional desktop) shortcuts are created.
-   **And** no installation errors are reported.

### AC3: Application Launch & Core Functionality
-   **Given** Fava has been successfully installed.
-   **When** Fava is launched via a shortcut or the executable.
-   **Then** the Fava application starts and the main interface is accessible (e.g., in a web browser if it's a web application).
-   **And** a sample Beancount file can be loaded and viewed.
-   **And** core reports (e.g., Balance Sheet, Income Statement) are displayed correctly.

### AC4: PQC Feature Functionality
-   **Given** the installed Fava application is running.
-   **When** PQC-specific features are utilized (e.g., selecting a PQC algorithm for a relevant operation, viewing data that relies on PQC hashing).
-   **Then** the PQC features operate as designed without errors.
-   **And** if applicable, PQC cryptographic operations (e.g., key generation, encryption, decryption, signature verification with PQC algorithms) complete successfully using the bundled libraries.
-   **And** frontend PQC WASM modules load and function correctly.

### AC5: Dependency Integrity
-   **Given** the installed Fava application is running.
-   **When** various features are used.
-   **Then** no errors occur due to missing Python modules, C extensions (like `oqs-python`), DLLs (like `liboqs.dll`), or frontend assets.

### AC6: Uninstallation
-   **Given** Fava has been successfully installed.
-   **When** the uninstallation process is initiated from "Add or remove programs".
-   **Then** the Fava application and its associated installed files (excluding user data) are completely removed from the system.
-   **And** shortcuts are removed.
-   **And** no uninstallation errors are reported.

## 4. Out of Scope for this Specification (unless explicitly included later)
-   Auto-update functionality for the installed application.
-   Support for Windows versions older than Windows 10 or 32-bit architectures.
-   Complex server-side PQC-TLS setup by the installer (focus is on client-side/local Fava operation).
-   Installer localization beyond English.