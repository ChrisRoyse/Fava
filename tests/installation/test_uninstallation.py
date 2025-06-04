"""
Tests for the Fava Windows Installer Uninstallation Process.

This script will contain checks and potentially automated routines
to verify that the uninstaller works correctly as per:
docs/test-plans/PQC_Windows_EXE_Installer_Test_Plan.md (Section 4.6)

Note: Automating uninstallation UI can be complex. These might initially
be manual checklists or use system commands to check for file removal.
"""

import unittest
import os
import subprocess
import platform
import shutil # For creating dummy user data

# Configuration
# These paths would be confirmed during/after installation tests.
INSTALLED_APP_DIR_PROGRAM_FILES = "C:\\Program Files\\FavaPQC"
INSTALLED_APP_DIR_USER_APPDATA = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "FavaPQC")
# Actual installed path might need to be dynamically determined or passed from installation tests
ACTUAL_INSTALL_PATH = INSTALLED_APP_DIR_PROGRAM_FILES # Default to one for placeholder logic

START_MENU_PROGRAMS_PATH = os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs")
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
FAVA_SHORTCUT_NAME = "FavaPQC.lnk" # Example, actual name might vary

DUMMY_USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "FavaTestData")
DUMMY_BEANCOUNT_FILE = os.path.join(DUMMY_USER_DATA_DIR, "my_finances.beancount")

class TestUninstallation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if platform.system() != "Windows":
            raise unittest.SkipTest("Uninstallation tests are Windows-specific.")
        # These tests assume Fava has been installed by a previous test phase.
        # A robust setup would check if ACTUAL_INSTALL_PATH exists.
        if not os.path.isdir(ACTUAL_INSTALL_PATH):
            print(f"Warning: Assumed Fava install path '{ACTUAL_INSTALL_PATH}' not found. Uninstallation tests might not be meaningful.")

        # Create dummy user data that should NOT be deleted
        os.makedirs(DUMMY_USER_DATA_DIR, exist_ok=True)
        with open(DUMMY_BEANCOUNT_FILE, "w") as f:
            f.write("2023-01-01 open Assets:Cash USD\n")

    @classmethod
    def tearDownClass(cls):
        # Clean up dummy user data
        if os.path.exists(DUMMY_BEANCOUNT_FILE):
            os.remove(DUMMY_BEANCOUNT_FILE)
        if os.path.exists(DUMMY_USER_DATA_DIR):
            try:
                os.rmdir(DUMMY_USER_DATA_DIR) # Fails if not empty, which is fine
            except OSError:
                pass


    def get_uninstall_command(self):
        """
        Placeholder: Retrieves the command to silently uninstall Fava.
        This usually involves finding the UninstallString in the registry.
        Example registry path:
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\[AppName]_is1"
        "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\[AppName]_is1"
        The specific key name depends on the installer tool (Inno Setup, NSIS).
        """
        # For Inno Setup, it's often like:
        # "C:\Program Files\FavaPQC\unins000.exe" /SILENT
        uninstaller_exe = os.path.join(ACTUAL_INSTALL_PATH, "unins000.exe") # Common for Inno Setup
        if os.path.exists(uninstaller_exe):
            return [uninstaller_exe, "/SILENT"] # /VERYSILENT for no progress
        return None

    def test_uninstallation_completes_placeholder(self):
        """
        Test Case ID: TP-UNINSTALL-001 (Partial - focuses on file removal)
        Verifies that the uninstallation process runs and removes application files.
        """
        uninstall_command = self.get_uninstall_command()
        if not uninstall_command:
            self.skipTest("Could not determine uninstallation command (unins000.exe not found or logic missing). Manual check required.")

        if not os.path.isdir(ACTUAL_INSTALL_PATH):
            self.skipTest(f"Fava does not appear to be installed at {ACTUAL_INSTALL_PATH}. Skipping uninstallation test.")

        try:
            print(f"Attempting to run uninstaller: {' '.join(uninstall_command)}")
            # Note: Running uninstaller might require admin rights if installed to Program Files.
            # This test might need to be run with elevated privileges.
            process = subprocess.run(uninstall_command, check=True, capture_output=True, timeout=120)
            print("Uninstaller STDOUT:", process.stdout.decode(errors='ignore'))
            print("Uninstaller STDERR:", process.stderr.decode(errors='ignore'))
        except FileNotFoundError:
            self.fail(f"Uninstaller executable not found: {uninstall_command[0]}")
        except subprocess.CalledProcessError as e:
            self.fail(f"Uninstallation command failed with exit code {e.returncode}.\nStdout: {e.stdout.decode(errors='ignore')}\nStderr: {e.stderr.decode(errors='ignore')}")
        except subprocess.TimeoutExpired:
            self.fail("Uninstallation command timed out.")

        # Verify application directory is removed
        # Need to wait a bit for uninstaller to finish file operations
        import time
        time.sleep(5) # Allow time for file system changes
        self.assertFalse(os.path.isdir(ACTUAL_INSTALL_PATH),
                         f"Application directory '{ACTUAL_INSTALL_PATH}' still exists after uninstallation.")

    def test_shortcuts_removed_placeholder(self):
        """
        Test Case ID: TP-UNINSTALL-001 (Partial - focuses on shortcut removal)
        Verifies Start Menu and Desktop shortcuts are removed.
        """
        # This test should run AFTER the uninstaller.
        start_menu_shortcut = os.path.join(START_MENU_PROGRAMS_PATH, "FavaPQC", FAVA_SHORTCUT_NAME) # Path might vary
        desktop_shortcut = os.path.join(DESKTOP_PATH, FAVA_SHORTCUT_NAME)

        # Might need to adjust for how Inno Setup/NSIS create Start Menu folders
        self.assertFalse(os.path.exists(start_menu_shortcut),
                         f"Start Menu shortcut '{start_menu_shortcut}' still exists after uninstallation.")
        self.assertFalse(os.path.exists(os.path.join(START_MENU_PROGRAMS_PATH, "FavaPQC")), # Check folder too
                         f"Start Menu folder for FavaPQC still exists after uninstallation.")
        self.assertFalse(os.path.exists(desktop_shortcut),
                         f"Desktop shortcut '{desktop_shortcut}' still exists after uninstallation (if it was created).")
        self.skipTest("Placeholder: Shortcut removal verification needs precise shortcut paths and to run post-uninstallation.")


    def test_user_data_not_deleted(self):
        """
        Test Case ID: TP-UNINSTALL-002
        Verifies that user-generated data is not deleted during uninstallation.
        """
        # This test relies on setUpClass creating dummy data.
        # It should be run AFTER the uninstallation process.
        self.assertTrue(os.path.exists(DUMMY_BEANCOUNT_FILE),
                        f"Dummy user data file '{DUMMY_BEANCOUNT_FILE}' was deleted during uninstallation.")
        self.assertTrue(os.path.isdir(DUMMY_USER_DATA_DIR),
                        f"Dummy user data directory '{DUMMY_USER_DATA_DIR}' was deleted during uninstallation.")

if __name__ == '__main__':
    # Ensure these tests are run after Fava has been installed and then uninstalled (or mock uninstallation)
    # For now, it's structured to be run after an uninstallation attempt.
    unittest.main()