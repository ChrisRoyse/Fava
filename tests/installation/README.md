# Fava Windows Installer Tests

This directory contains scripts and resources for testing the Fava Windows `.exe` installer.
The tests aim to verify:
-   Successful build of the installer.
-   Correct installation flow on target Windows systems.
-   Full functionality of the installed Fava application, including PQC features.
-   Proper uninstallation.

Refer to [`docs/test-plans/PQC_Windows_EXE_Installer_Test_Plan.md`](docs/test-plans/PQC_Windows_EXE_Installer_Test_Plan.md) for detailed test cases.

## Test Scripts

-   `test_build.py`: Scripts/checks related to the installer build process.
-   `test_installation_flow.py`: Scripts/checks for the installation process itself.
-   `test_app_functionality.py`: Scripts/checks for verifying the installed application's functionality.
-   `test_uninstallation.py`: Scripts/checks for the uninstallation process.

These scripts may be a combination of automated routines (e.g., using UI automation tools or scripting languages) and manual check procedures.