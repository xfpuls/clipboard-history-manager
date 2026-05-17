"""Main application class that wires all components together."""
import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from clipboard_manager.config import load_config, save_config
from clipboard_manager.database import init_db, cleanup
from clipboard_manager.clipboard_monitor import ClipboardMonitor
from clipboard_manager.hotkey import HotkeyFilter
from clipboard_manager.ui.styles import APP_STYLE
from clipboard_manager.ui.main_panel import MainPanel
from clipboard_manager.ui.history_window import HistoryWindow
from clipboard_manager.ui.settings_page import SettingsPage
from clipboard_manager.ui.tray import TrayManager, set_auto_start, _get_icon_path
from clipboard_manager.updater import check_update


class MainWindow(QWidget):
    def __init__(self, hide_to_tray, quit_app):
        super().__init__()
        self._hide_to_tray = hide_to_tray
        self._quit_app = quit_app
        self.setWindowTitle('剪贴板历史管理器')
        self.setFixedSize(400, 560)
        icon_path = _get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)

        # Central stack for page navigation
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Pages
        self.main_panel = MainPanel()
        self.history_window = HistoryWindow()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.main_panel)      # index 0
        self.stack.addWidget(self.history_window)   # index 1
        self.stack.addWidget(self.settings_page)    # index 2

        # Wire navigation
        self.main_panel.show_settings.connect(lambda: self.stack.setCurrentIndex(2))
        self.main_panel.show_history.connect(self._show_history)
        self.main_panel.minimize_to_tray.connect(self._hide_to_tray)
        self.main_panel.quit_app.connect(self._quit_app)

        self.history_window.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.settings_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.settings_page.hotkey_change_requested.connect(self._start_hotkey_change)

        # Start on main panel
        self.stack.setCurrentIndex(0)

    def closeEvent(self, event):
        """System X quits the application completely."""
        self._quit_app()

    def _show_history(self):
        self.history_window.current_page = 1
        self.history_window.refresh()
        self.stack.setCurrentIndex(1)

    def _start_hotkey_change(self):
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle('修改快捷键')
        msg.setText('请在 5 秒内按下新的快捷键组合')
        msg.setInformativeText('例如: Ctrl+Shift+X, Ctrl+Alt+V 等')
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.show()
        QTimer.singleShot(5000, msg.close)


class ClipboardApp:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.app.setStyleSheet(APP_STYLE)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize database
        init_db()
        config = load_config()
        cleanup(config.storage_days, config.max_items)

        # Clipboard monitor
        self.monitor = ClipboardMonitor()

        # Main window
        self.window = MainWindow(
            hide_to_tray=lambda: self.window.hide(),
            quit_app=self._quit,
        )

        # System tray
        self.tray = TrayManager(
            show_panel=self._show_panel,
            show_history=self._show_history_window,
            show_settings=self._show_settings,
            quit_app=self._quit
        )
        self.tray.show()

        # Global hotkey
        self.hotkey_filter = HotkeyFilter()
        self.hotkey_filter.hotkey_triggered.connect(self._toggle_panel)
        self.app.installNativeEventFilter(self.hotkey_filter)
        self._reregister_hotkey(config.hotkey)

        # Set auto-start based on config
        if config.auto_start:
            set_auto_start(True)

        # Check for updates (background, delayed)
        QTimer.singleShot(3000, self._check_updates)

        # Show panel on startup
        self._show_panel()

    def _show_panel(self):
        self.window.stack.setCurrentIndex(0)
        self.window.main_panel.refresh()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _show_history_window(self):
        self.window.history_window.current_page = 1
        self.window.history_window.refresh()
        self.window.stack.setCurrentIndex(1)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _show_settings(self):
        self.window.stack.setCurrentIndex(2)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _toggle_panel(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self._show_panel()

    def _reregister_hotkey(self, hotkey_str: str):
        ok = self.hotkey_filter.register(hotkey_str)
        if not ok:
            self.hotkey_filter.register('Ctrl+Shift+V')

    def _check_updates(self):
        config = load_config()
        info = check_update(config.last_version)
        if info and info['version'] != config.skip_version:
            self._show_update_notification(info)

    def _show_update_notification(self, info: dict):
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self.window)
        msg.setWindowTitle('软件更新')
        msg.setText(f'发现新版本 v{info["version"]}')
        msg.setInformativeText(
            f'当前版本: v{load_config().last_version}\n\n'
            f'更新内容:\n{info.get("notes", "优化体验，修复问题")}'
        )
        update_btn = msg.addButton('立即更新', QMessageBox.YesRole)
        later_btn = msg.addButton('稍后提醒', QMessageBox.NoRole)
        msg.setDefaultButton(update_btn)
        msg.exec()

        if msg.clickedButton() == update_btn:
            from clipboard_manager.updater import download_and_install
            download_and_install(info)
        else:
            config = load_config()
            config.skip_version = info['version']
            save_config(config)

    def _quit(self):
        """Fully quit the application - stop all timers, clean up, force exit."""
        if hasattr(self.window.main_panel, '_refresh_timer'):
            self.window.main_panel._refresh_timer.stop()
        self.hotkey_filter.unregister()
        self.tray.hide()
        self.window.hide()
        self.app.closeAllWindows()
        self.app.exit(0)
        os._exit(0)

    def run(self):
        self.app.exec()
