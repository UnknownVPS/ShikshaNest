import os
import sys
import platform
import requests
import shutil
from subprocess import Popen
from PyQt5.QtWidgets import QMessageBox, QApplication

GITHUB_REPO_OWNER = 'unknownpersonog'
GITHUB_REPO_NAME = 'fedrock'
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest'

class UpdateManager:
    @staticmethod
    def check_for_updates(current_version):
        try:
            # Fetch latest release info from GitHub API
            response = requests.get(GITHUB_API_URL)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version_str = latest_release['tag_name']  # Assuming tag_name follows versioning convention

                # Parse version strings into comparable components
                current_version_parts = UpdateManager.parse_version(current_version)
                latest_version_parts = UpdateManager.parse_version(latest_version_str)

                # Compare versions
                if latest_version_parts > current_version_parts:
                    # Prompt user to confirm update
                    reply = QMessageBox.question(None, "Update Available", "An update is available. Do you want to update?",
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        download_url = UpdateManager.get_download_url_for_os(latest_release)
                        if download_url:
                            if UpdateManager.download_and_replace_executable(download_url):
                                return True
                    else:
                        return False  # User declined update
                else:
                    QMessageBox.information(None, "Update Check", "You are already using the latest version.")
            else:
                QMessageBox.warning(None, "Update Check", "Failed to check for updates.")
        except Exception as e:
            QMessageBox.critical(None, "Update Check", f"Error checking for updates: {e}")
        return False

    @staticmethod
    def parse_version(version_str):
        # Example version format: vyear.month.day.build
        version_str = version_str.lstrip('v')  # Remove 'v' prefix
        parts = version_str.split('.')
        return tuple(map(int, parts))  # Convert parts to integers for comparison

    @staticmethod
    def get_download_url_for_os(latest_release):
        # Determine which OS the application is running on
        if platform.system() == 'Windows':
            asset_name = 'main_windows.exe'
        elif platform.system() == 'Linux':
            asset_name = 'main_linux.bin'
        else:
            QMessageBox.warning(None, "Update", "Unsupported operating system.")
            return None

        # Find the correct asset for the current OS
        for asset in latest_release['assets']:
            if asset['name'] == asset_name:
                return asset['browser_download_url']

        QMessageBox.warning(None, "Update", f"No executable found for {platform.system()}.")
        return None

    @staticmethod
    def download_and_replace_executable(download_url):
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Save the new executable to a temporary file
            new_executable_path = './update_new'
            with open(new_executable_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                
            # Replace the current executable and set executable permissions
            UpdateManager.replace_executable(new_executable_path)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Update", f"Failed to download update: {e}")
            return False

    @staticmethod
    def replace_executable(new_executable_path):
        current_executable = sys.executable
        try:
            # Remove the old executable and replace it with the new one
            os.remove(current_executable)
            shutil.move(new_executable_path, current_executable)
            
            # Set executable permissions for the new executable
            if platform.system() != 'Windows':
                os.chmod(current_executable, 0o755)  # Ensure executable on Linux

            QMessageBox.information(None, "Successful Update", f"Update was successful, please restart application!")
        except Exception as e:
            QMessageBox.critical(None, "Update", f"Failed to replace executable: {e}")