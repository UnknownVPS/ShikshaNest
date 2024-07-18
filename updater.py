import os
import sys
import platform
import requests
import shutil
from subprocess import Popen
from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog

GITHUB_REPO_OWNER = 'unknownpersonog'
GITHUB_REPO_NAME = 'fedrock'
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest'

class UpdateManager:
    @staticmethod
    def check_for_updates(current_version):
        try:
            response = requests.get(GITHUB_API_URL)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version_str = latest_release['tag_name']

                current_version_parts = UpdateManager.parse_version(current_version)
                latest_version_parts = UpdateManager.parse_version(latest_version_str)

                if latest_version_parts > current_version_parts:
                    reply = QMessageBox.question(None, "Update Available", 
                                                 "An update is available. Do you want to update?",
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        download_url = UpdateManager.get_download_url_for_os(latest_release)
                        if download_url:
                            if UpdateManager.download_and_save_executable(download_url):
                                return True
                    else:
                        return False
                else:
                    QMessageBox.information(None, "Update Check", "You are already using the latest version.")
            else:
                QMessageBox.warning(None, "Update Check", "Failed to check for updates.")
        except Exception as e:
            QMessageBox.critical(None, "Update Check", f"Error checking for updates: {e}")
        return False

    @staticmethod
    def parse_version(version_str):
        version_str = version_str.lstrip('v')
        parts = version_str.split('.')
        return tuple(map(int, parts))

    @staticmethod
    def get_download_url_for_os(latest_release):
        if platform.system() == 'Windows':
            asset_name = 'main_windows.exe'
        elif platform.system() == 'Linux':
            asset_name = 'main_linux.bin'
        else:
            QMessageBox.warning(None, "Update", "Unsupported operating system.")
            return None

        for asset in latest_release['assets']:
            if asset['name'] == asset_name:
                return asset['browser_download_url']

        QMessageBox.warning(None, "Update", f"No executable found for {platform.system()}.")
        return None

    @staticmethod
    def download_and_save_executable(download_url):
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            if platform.system() == 'Windows':
                default_filename = 'Fedrock.exe'
                file_filter = "Executable (*.exe)"
            elif platform.system() == 'Linux':
                default_filename = 'Fedrock'
                file_filter = "Executable (*)"
            else:
                QMessageBox.warning(None, "Update", "Unsupported operating system.")
                return False

            save_path, _ = QFileDialog.getSaveFileName(
                None, "Save Updated Executable", default_filename, file_filter
            )

            if not save_path:
                QMessageBox.information(None, "Update Cancelled", "Update was cancelled.")
                return False

            with open(save_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            if platform.system() == 'Linux':
                os.chmod(save_path, 0o755)  # Make the file executable on Linux

            QMessageBox.information(None, "Successful Update", 
                                    f"Update was successful. The new version has been saved as:\n{save_path}\n\n"
                                    "Please restart the application using this new file.")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Update", f"Failed to download update: {e}")
            return False