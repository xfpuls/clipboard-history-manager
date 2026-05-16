"""Main clipboard panel - search, filter, card list, and always-on-top toggle."""
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QLabel, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QClipboard, QIcon

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
        self._always_on_top = True
        self._build_ui()
        self.refresh()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(2000)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 10)
        main_layout.setSpacing(8)

        # === Title bar row: app name + minimize/close ===
        title_row = QHBoxLayout()
        title_row.setSpacing(4)

        title_lbl = QLabel('剪贴板历史管理器')
        title_lbl.setStyleSheet('font-size: 13px; font-weight: 600; color: #5B9BD5;')
        title_row.addWidget(title_lbl)
        title_row.addStretch()

        # Minimize button
        min_btn = QPushButton('—')
        min_btn.setFixedSize(28, 28)
        min_btn.setStyleSheet(
            'QPushButton { background: white; color: #5C7DA0; border: 1px solid #D0DFEF; '
            'border-radius: 6px; font-size: 12px; font-weight: bold; }'
            'QPushButton:hover { background: #E3F2FD; }'
        )
        min_btn.setToolTip('最小化到托盘')
        min_btn.clicked.connect(self.minimize_to_tray.emit)
        title_row.addWidget(min_btn)

        # Close button
        close_btn = QPushButton('✕')
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(
            'QPushButton { background: white; color: #E74C3C; border: 1px solid #D0DFEF; '
            'border-radius: 6px; font-size: 12px; font-weight: bold; }'
            'QPushButton:hover { background: #FDEDEC; }'
        )
        close_btn.setToolTip('退出软件')
        close_btn.clicked.connect(self.quit_app.emit)
        title_row.addWidget(close_btn)

        main_layout.addLayout(title_row)

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
        self.pin_top_btn.setChecked(True)
        self.pin_top_btn.setToolTip('窗口置顶：开')
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
        # Find the parent window and toggle the flag
        w = self.window()
        if w:
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
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.search_text or self.current_filter != 'all':
            records, _, _ = get_records(
                search=self.search_text, filter_type=self.current_filter, page=0
            )
        else:
            records = get_recent(20)

        for rec in records:
            card = CardWidget(rec)
            card.clicked.connect(self._on_card_click)
            card.pin_toggled.connect(lambda rid, val: self.refresh())
            card.deleted.connect(lambda rid: self.refresh())
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _on_card_click(self, record: dict):
        clipboard = QApplication.instance().clipboard()
        if record['type'] == 'text' and record.get('content'):
            clipboard.setText(record['content'])
        elif record['type'] == 'image' and record.get('image_data'):
            from PySide6.QtGui import QImage
            img = QImage()
            img.loadFromData(record['image_data'])
            clipboard.setImage(img)
