"""Update checker - queries GitHub Releases, notifies user of new versions."""
import webbrowser
from typing import Optional
import requests

GITHUB_REPO = 'xfpuls/clipboard-history-manager'
API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
RELEASES_URL = f'https://github.com/{GITHUB_REPO}/releases'


def _parse_version(version_str: str) -> tuple:
    v = version_str.lstrip('v')
    parts = [int(p) for p in v.split('.')[:3]]
    return tuple(parts)


def check_update(current_version: str) -> Optional[dict]:
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
                }
    except Exception:
        pass
    return None


def open_releases_page():
    """Open the GitHub Releases page in the browser."""
    webbrowser.open(RELEASES_URL)
