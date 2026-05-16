"""System tray icon and menu."""
import os
import sys
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QObject


def _get_icon_path() -> str:
    """Get the path to the icon file, works in dev and PyInstaller exe."""
    if getattr(sys, 'frozen', False):
        # PyInstaller --onefile extracts data to sys._MEIPASS
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, 'clipboard_icon.ico')


def _create_tray_icon() -> QIcon:
    path = _get_icon_path()
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()


def set_auto_start(enabled: bool):
    import winreg
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            exe_path = sys.executable
            if not exe_path.endswith('.exe'):
                script = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, 'ClipboardManager', 0, winreg.REG_SZ,
                                  f'"{sys.executable}" "{script}"')
            else:
                winreg.SetValueEx(key, 'ClipboardManager', 0, winreg.REG_SZ, f'"{exe_path}"')
        else:
            try:
                winreg.DeleteValue(key, 'ClipboardManager')
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass


class TrayManager(QObject):
    def __init__(self, show_panel, show_history, show_settings, quit_app):
        super().__init__()
        self._show_panel = show_panel
        self._show_history = show_history

        self.icon = QSystemTrayIcon(self)
        self.icon.setIcon(_create_tray_icon())
        self.icon.setToolTip('剪贴板历史管理器')

        # Build menu - parent=self keeps it alive
        self._menu = QMenu()
        self._menu.setStyleSheet('''
            QMenu {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
                font-family: "Microsoft YaHei";
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                color: #2C3E50;
            }
            QMenu::item:selected {
                background: #E3F2FD;
            }
            QMenu::separator {
                height: 1px;
                background: #F0F0F0;
                margin: 4px 8px;
            }
        ''')

        self._panel_action = QAction('📋 打开面板', self)
        self._panel_action.triggered.connect(show_panel)
        self._menu.addAction(self._panel_action)

        self._history_action = QAction('📖 历史记录', self)
        self._history_action.triggered.connect(show_history)
        self._menu.addAction(self._history_action)

        self._settings_action = QAction('⚙ 设置', self)
        self._settings_action.triggered.connect(show_settings)
        self._menu.addAction(self._settings_action)

        self._menu.addSeparator()

        quit_icon = QAction('退出', self)
        quit_icon.setData('quit')
        quit_icon.triggered.connect(quit_app)
        self._menu.addAction(quit_icon)

        # Style the quit item red
        self._quit_action = quit_icon

        self.icon.setContextMenu(self._menu)
        self.icon.activated.connect(self._on_activate)

    def _on_activate(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._show_panel()

    def show(self):
        self.icon.show()

    def hide(self):
        self.icon.hide()
