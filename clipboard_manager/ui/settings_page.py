"""Settings page - storage, limits, hotkey, auto-start, updates."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QButtonGroup, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from clipboard_manager.config import AppConfig, load_config, save_config
from clipboard_manager.updater import check_update


class OptionRow(QWidget):
    value_changed = Signal(str)

    def __init__(self, title: str, options: list, current: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        for i, (label, val) in enumerate(options):
            btn = QPushButton(label)
            btn.setObjectName('optionBtn')
            btn.setCheckable(True)
            if val == current:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, v=val: self.value_changed.emit(v))
            self.btn_group.addButton(btn, i)
            layout.addWidget(btn)


class ToggleRow(QWidget):
    toggled = Signal(bool)

    def __init__(self, title: str, hint: str, on: bool = True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        text_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setObjectName('sectionTitle')
        text_layout.addWidget(title_lbl)
        hint_lbl = QLabel(hint)
        hint_lbl.setObjectName('hintLabel')
        hint_lbl.setWordWrap(True)
        text_layout.addWidget(hint_lbl)
        layout.addLayout(text_layout)

        layout.addStretch()

        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(44, 24)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(on)
        self._update_style()
        self.toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_btn)

    def _update_style(self):
        on = self.toggle_btn.isChecked()
        bg = '#5B9BD5' if on else '#C0D0E0'
        self.toggle_btn.setStyleSheet(
            f'QPushButton {{ background: {bg}; border-radius: 12px; padding: 0; }}'
        )

    def _toggle(self):
        self._update_style()
        self.toggled.emit(self.toggle_btn.isChecked())


class WrapLabel(QLabel):
    """Label that always wraps text."""
    def __init__(self, text: str, obj_name: str = ''):
        super().__init__(text)
        if obj_name:
            self.setObjectName(obj_name)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class SettingsPage(QWidget):
    back_clicked = Signal()
    hotkey_change_requested = Signal()

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton('← 返回')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(back_btn)
        title = QLabel('设置')
        title.setObjectName('pageTitle')
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Storage days
        card1 = QFrame()
        card1.setObjectName('card')
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(14, 12, 14, 12)
        c1_layout.setSpacing(6)
        c1_layout.addWidget(WrapLabel('保存期限', 'sectionTitle'))
        self.days_row = OptionRow(
            '', [('1 天', '1'), ('3 天', '3'), ('5 天', '5')],
            str(self.config.storage_days)
        )
        self.days_row.value_changed.connect(self._on_days_changed)
        c1_layout.addWidget(self.days_row)
        c1_layout.addWidget(WrapLabel('超过期限的剪贴记录将自动删除', 'hintLabel'))
        layout.addWidget(card1)

        # Max items
        card2 = QFrame()
        card2.setObjectName('card')
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(14, 12, 14, 12)
        c2_layout.setSpacing(6)
        c2_layout.addWidget(WrapLabel('数量上限', 'sectionTitle'))
        self.count_row = OptionRow(
            '', [('200 条', '200'), ('500 条', '500'), ('1000 条', '1000')],
            str(self.config.max_items)
        )
        self.count_row.value_changed.connect(self._on_count_changed)
        c2_layout.addWidget(self.count_row)
        c2_layout.addWidget(WrapLabel('超过上限自动删除最早的记录', 'hintLabel'))
        layout.addWidget(card2)

        # Hotkey
        card3 = QFrame()
        card3.setObjectName('card')
        c3_layout = QVBoxLayout(card3)
        c3_layout.setContentsMargins(14, 12, 14, 12)
        c3_layout.setSpacing(6)
        c3_layout.addWidget(WrapLabel('全局快捷键', 'sectionTitle'))
        hotkey_row = QHBoxLayout()
        hotkey_display = QLabel(self.config.hotkey)
        hotkey_display.setStyleSheet(
            'background: #F5F7FA; border-radius: 8px; padding: 8px 12px;'
            'font-size: 13px; color: #2C3E50; letter-spacing: 1px;'
        )
        hotkey_row.addWidget(hotkey_display)
        modify_btn = QPushButton('修改')
        modify_btn.setStyleSheet(
            'QPushButton { background: white; color: #5B9BD5; border: 1px solid #5B9BD5; '
            'border-radius: 8px; padding: 8px 12px; font-size: 12px; }'
            'QPushButton:hover { background: #E3F2FD; }'
        )
        modify_btn.clicked.connect(self.hotkey_change_requested.emit)
        hotkey_row.addWidget(modify_btn)
        hotkey_row.addStretch()
        c3_layout.addLayout(hotkey_row)
        c3_layout.addWidget(WrapLabel('在任何应用中按下此组合键呼出面板', 'hintLabel'))
        layout.addWidget(card3)

        # Auto start
        card4 = QFrame()
        card4.setObjectName('card')
        c4_layout = QVBoxLayout(card4)
        c4_layout.setContentsMargins(14, 12, 14, 12)
        self.auto_start_row = ToggleRow('开机自启', '电脑启动时自动运行', self.config.auto_start)
        self.auto_start_row.toggled.connect(self._on_auto_start)
        c4_layout.addWidget(self.auto_start_row)
        layout.addWidget(card4)

        # Update
        card5 = QFrame()
        card5.setObjectName('card')
        c5_layout = QVBoxLayout(card5)
        c5_layout.setContentsMargins(14, 12, 14, 12)
        update_row = QHBoxLayout()
        update_text = QVBoxLayout()
        update_text.addWidget(WrapLabel('软件更新', 'sectionTitle'))
        self.update_hint = WrapLabel(f'当前版本 v{self.config.last_version}', 'hintLabel')
        update_text.addWidget(self.update_hint)
        update_row.addLayout(update_text)
        update_row.addStretch()
        self.check_update_btn = QPushButton('检查更新')
        self.check_update_btn.setStyleSheet(
            'QPushButton { background: white; color: #5B9BD5; border: 1px solid #5B9BD5; '
            'border-radius: 8px; padding: 6px 12px; font-size: 12px; }'
            'QPushButton:hover { background: #E3F2FD; }'
        )
        self.check_update_btn.clicked.connect(self._check_update)
        update_row.addWidget(self.check_update_btn)
        c5_layout.addLayout(update_row)
        layout.addWidget(card5)

        # About
        card6 = QFrame()
        card6.setObjectName('card')
        c6_layout = QHBoxLayout(card6)
        c6_layout.setContentsMargins(14, 12, 14, 12)
        about_text = QVBoxLayout()
        about_text.addWidget(WrapLabel('关于', 'sectionTitle'))
        about_text.addWidget(WrapLabel('剪贴板历史管理器 v' + self.config.last_version, 'hintLabel'))
        c6_layout.addLayout(about_text)
        c6_layout.addStretch()
        layout.addWidget(card6)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _on_days_changed(self, val: str):
        self.config.storage_days = int(val)
        save_config(self.config)

    def _on_count_changed(self, val: str):
        self.config.max_items = int(val)
        save_config(self.config)

    def _on_auto_start(self, on: bool):
        self.config.auto_start = on
        save_config(self.config)
        from clipboard_manager.ui.tray import set_auto_start
        set_auto_start(on)

    def _check_update(self):
        self.check_update_btn.setText('检查中...')
        self.check_update_btn.setEnabled(False)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self._do_update_check)

    def _do_update_check(self):
        info = check_update(self.config.last_version)
        self.check_update_btn.setText('检查更新')
        self.check_update_btn.setEnabled(True)

        if info:
            self.update_hint.setText(f'发现新版本 v{info["version"]}')
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle('软件更新')
            msg.setText(f'发现新版本 v{info["version"]}')
            msg.setInformativeText(
                f'当前版本: v{self.config.last_version}\n\n'
                f'更新内容:\n{info.get("notes", "优化体验，修复问题")}\n\n'
                f'是否立即更新？'
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.button(QMessageBox.Yes).setText('立即更新')
            msg.button(QMessageBox.No).setText('稍后提醒')
            if msg.exec() == QMessageBox.Yes:
                from clipboard_manager.updater import download_and_install
                download_and_install(info)
        else:
            self.update_hint.setText(f'已是最新版本 v{self.config.last_version} ✓')
