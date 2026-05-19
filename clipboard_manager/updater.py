"""Update checker - queries GitHub Releases API, downloads and installs automatically."""
import os
import sys
import tempfile
from typing import Optional
import requests

GITHUB_REPO = 'xfpuls/clipboard-history-manager'
API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'


def _parse_version(version_str: str) -> tuple:
    v = version_str.lstrip('v')
    parts = [int(p) for p in v.split('.')[:3]]
    return tuple(parts)


def check_update(current_version: str) -> Optional[dict]:
    """Check GitHub for a newer version. Returns release info dict or None."""
    try:
        resp = requests.get(API_URL, timeout=10)
        if resp.status_code == 200:
            release = resp.json()
            remote_ver = _parse_version(release.get('tag_name', '0.0.0'))
            local_ver = _parse_version(current_version)
            if remote_ver > local_ver:
                return {
                    'version': release.get('tag_name', '').lstrip('v'),
                    'notes': release.get('body', ''),
                    'url': release.get('html_url', ''),
                    'assets': release.get('assets', []),
                }
    except Exception:
        pass
    return None


def _download_with_progress(url: str, dest: str, callback=None) -> bool:
    """Download a file to dest, optionally calling callback(bytes_done, total)."""
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        done = 0
        with open(dest, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                done += len(chunk)
                if callback and total:
                    callback(done, total)
        return True
    except Exception:
        return False


def _create_upgrade_script(new_exe: str, target_exe: str) -> str:
    """Create a batch script that replaces the exe and restarts the app."""
    script = os.path.join(tempfile.gettempdir(), 'clipboard_upgrade.bat')
    with open(script, 'w') as f:
        f.write('@echo off\n')
        f.write('title 正在更新剪贴板历史管理器...\n')
        f.write('echo 正在安装更新，请稍候...\n')
        # Wait for the old process to exit
        f.write('timeout /t 2 /nobreak >nul\n')
        # Kill any lingering process
        f.write('taskkill /f /im clipboard_manager.exe >nul 2>&1\n')
        f.write('timeout /t 1 /nobreak >nul\n')
        # Move new exe over old
        f.write(f'copy /y "{new_exe}" "{target_exe}" >nul\n')
        # Clean up temp
        f.write(f'del /f /q "{new_exe}" >nul 2>&1\n')
        # Launch new version
        f.write(f'start "" "{target_exe}"\n')
        # Self-destruct
        f.write('del /f /q "%~f0"\n')
    return script


def download_and_install(info: dict):
    """Download the new exe and install it, replacing the current version."""
    assets = info.get('assets', [])
    if not assets:
        return

    # Find the .exe asset
    exe_asset = None
    for a in assets:
        name = a.get('name', '')
        if name.endswith('.exe'):
            exe_asset = a
            break

    if not exe_asset:
        return

    download_url = exe_asset.get('browser_download_url', '')
    if not download_url:
        return

    # Determine target paths
    if getattr(sys, 'frozen', False):
        current_exe = sys.executable
    else:
        current_exe = os.path.abspath(sys.argv[0])

    tmp_file = os.path.join(tempfile.gettempdir(), 'clipboard_manager_new.exe')

    # Download the new version
    success = _download_with_progress(download_url, tmp_file)
    if not success:
        return

    # Create upgrade script and run it
    script = _create_upgrade_script(tmp_file, current_exe)
    os.startfile(script)

    # Quit the current instance
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    os._exit(0)
