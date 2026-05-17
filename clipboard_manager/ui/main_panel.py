"""Main clipboard panel - search, filter, card list, and always-on-top toggle."""
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QLabel, QButtonGroup, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from clipboard_manager.database import get_recent, get_records
from clipboard_manager.ui.card_widget import CardWidget


def _get_gear_icon_path() -> str:
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, 'gear_icon_32.png')


class FilterBar(QWidget):
    type_changed = Signal(str)
    history_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        filters = [('全部', 'all'), ('Aa 文字', 'text'), ('IMG 图片', 'image')]
        for i, (label, val) in enumerate(filters):
            btn = QPushButton(label)
            btn.setObjectName('filterBtn')
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, v=val: self.type_changed.emit(v))
            self.btn_group.addButton(btn, i)
            layout.addWidget(btn)

        layout.addStretch()

        hist_btn = QPushButton('📖 查看历史')
        hist_btn.setObjectName('historyBtn')
        hist_btn.clicked.connect(self.history_clicked.emit)
        layout.addWidget(hist_btn)


class MainPanel(QWidget):
    show_settings = Signal()
    show_history = Signal()
    minimize_to_tray = Signal()
    quit_app = Signal()

    def __init__(self):
        super().__init__()
        self.current_filter = 'all'
        self.search_text = ''
        self._always_on_top = False
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # === Search row: search + pin-top + settings ===
        search_row = QHBoxLayout()
        search_row.setSpacing(6)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('搜索历史记录...')
        self.search_box.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_box)

        self.pin_top_btn = QPushButton('📌')
        self.pin_top_btn.setFixedSize(32, 32)
        self.pin_top_btn.setCheckable(True)
        self.pin_top_btn.setChecked(False)
        self.pin_top_btn.setToolTip('窗口置顶：关')
        self.pin_top_btn.clicked.connect(self._toggle_always_on_top)
        self._update_pin_top_style()
        search_row.addWidget(self.pin_top_btn)

        settings_btn = QPushButton()
        settings_btn.setFixedSize(32, 32)
        settings_btn.setObjectName('settingsBtn')
        settings_btn.setToolTip('设置')
        gear_path = _get_gear_icon_path()
        if os.path.exists(gear_path):
            settings_btn.setIcon(QIcon(gear_path))
            settings_btn.setIconSize(settings_btn.size())
        else:
            settings_btn.setText('⚙')
        settings_btn.clicked.connect(self.show_settings.emit)
        search_row.addWidget(settings_btn)

        main_layout.addLayout(search_row)

        # Filter bar
        self.filter_bar = FilterBar()
        self.filter_bar.type_changed.connect(self._on_filter)
        self.filter_bar.history_clicked.connect(self.show_history.emit)
        main_layout.addWidget(self.filter_bar)

        # Scroll area for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(6)
        self.cards_layout.addStretch()

        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)

    def _update_pin_top_style(self):
        on = self.pin_top_btn.isChecked()
        if on:
            self.pin_top_btn.setStyleSheet(
                'QPushButton { background: #5B9BD5; color: white; border: none; '
                'border-radius: 6px; font-size: 14px; }'
                'QPushButton:hover { background: #4A8AC4; }'
            )
        else:
            self.pin_top_btn.setStyleSheet(
                'QPushButton { background: white; color: #C0D0E0; border: 1px solid #D0DFEF; '
                'border-radius: 6px; font-size: 14px; }'
                'QPushButton:hover { background: #E3F2FD; }'
            )

    def _toggle_always_on_top(self):
        on = self.pin_top_btn.isChecked()
        self._update_pin_top_style()
        self.pin_top_btn.setToolTip('窗口置顶：开' if on else '窗口置顶：关')
        w = self.window()
        if w:
            w.hide()
            flags = w.windowFlags()
            if on:
                w.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            else:
                w.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            w.show()

    def _on_search(self, text: str):
        self.search_text = text
        self.refresh()

    def _on_filter(self, ftype: str):
        self.current_filter = ftype
        self.refresh()

    def refresh(self):
        # Immediately clear all cards
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if self.search_text or self.current_filter != 'all':
            records, _, _ = get_records(
                search=self.search_text, filter_type=self.current_filter, page=0
            )
        else:
            records = get_recent(20)

        for rec in records:
            card = CardWidget(
                rec,
                on_click=self._on_card_click,
                on_pin_toggled=lambda rid, val: self.refresh(),
                on_deleted=lambda rid: self.refresh(),
            )
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _on_card_click(self, record: dict):
        if record['type'] == 'text' and record.get('content'):
            content = record['content']
            # Double-write: pyperclip first, then Qt as guarantee
            try:
                import pyperclip
                pyperclip.copy(content)
            except Exception:
                pass
            QApplication.instance().clipboard().setText(content)
        elif record['type'] == 'image' and record.get('image_data'):
            from PySide6.QtGui import QImage
            img = QImage()
            img.loadFromData(record['image_data'])
            QApplication.instance().clipboard().setImage(img)
