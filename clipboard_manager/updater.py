"""Update checker - queries GitHub Releases API."""
import threading
from typing import Optional
import requests

# Update this to your actual GitHub repo when publishing
GITHUB_REPO = 'xfpuls/clipboard-history-manager'
API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'


def _parse_version(version_str: str) -> tuple:
    """Parse 'v1.2.3' or '1.2.3' into (1, 2, 3)."""
    v = version_str.lstrip('v')
    parts = v.split('.')
    return tuple(int(p) for p in parts[:3])


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
                    'notes': release.get('body', '优化体验，修复问题'),
                    'url': release.get('html_url', ''),
                    'assets': release.get('assets', []),
                }
    except Exception:
        pass
    return None


def download_and_install(_info: dict):
    """Open the release page in the browser for manual download."""
    import webbrowser
    url = _info.get('url', f'https://github.com/{GITHUB_REPO}/releases')
    webbrowser.open(url)
