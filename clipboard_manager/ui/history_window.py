"""Paginated history window - 15 items per page."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QLabel, QButtonGroup, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage

from clipboard_manager.database import get_records
from clipboard_manager.ui.card_widget import CardWidget


class PageBar(QWidget):
    page_changed = Signal(int)

    def __init__(self, current: int, total: int):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self._current = current
        self._total = total

        self.prev_btn = QPushButton('◀ 上一页')
        self.prev_btn.setObjectName('pageBtn')
        self.prev_btn.setEnabled(current > 1)
        self.prev_btn.clicked.connect(lambda: self.page_changed.emit(current - 1))
        layout.addWidget(self.prev_btn)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.page_btns = []

        # Show up to 5 page numbers
        start = max(1, current - 2)
        end = min(total, start + 4)
        start = max(1, end - 4)

        for p in range(start, end + 1):
            btn = QPushButton(str(p))
            btn.setObjectName('pageBtn')
            btn.setCheckable(True)
            if p == current:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, pg=p: self.page_changed.emit(pg))
            self.btn_group.addButton(btn)
            self.page_btns.append(btn)
            layout.addWidget(btn)

        self.next_btn = QPushButton('下一页 ▶')
        self.next_btn.setObjectName('pageBtn')
        self.next_btn.setEnabled(current < total)
        self.next_btn.clicked.connect(lambda: self.page_changed.emit(current + 1))
        layout.addWidget(self.next_btn)


class HistoryWindow(QWidget):
    back_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.total_pages = 1
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton('← 返回')
        back_btn.setObjectName('backBtn')
        back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(back_btn)

        self.title_lbl = QLabel('全部历史记录')
        self.title_lbl.setObjectName('pageTitle')
        header.addWidget(self.title_lbl)

        header.addStretch()

        self.count_lbl = QLabel()
        self.count_lbl.setObjectName('hintLabel')
        header.addWidget(self.count_lbl)

        layout.addLayout(header)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(4)
        self.cards_layout.addStretch()

        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll)

        # Page bar
        self.page_bar_container = QWidget()
        self.page_bar_layout = QVBoxLayout(self.page_bar_container)
        self.page_bar_layout.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(self.page_bar_container)

        self.refresh()

    def _clear_page_bar(self):
        while self.page_bar_layout.count():
            item = self.page_bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def refresh(self):
        self._clear_cards()
        self._clear_page_bar()

        records, total, self.total_pages = get_records(page=self.current_page, per_page=15)
        self.count_lbl.setText(f'共 {total} 条')

        for rec in records:
            card = CardWidget(
                rec,
                on_click=self._on_card_click,
                on_pin_toggled=lambda rid, val: self.refresh(),
                on_deleted=lambda rid: self.refresh(),
            )
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        page_bar = PageBar(self.current_page, self.total_pages)
        page_bar.page_changed.connect(self._go_page)
        self.page_bar_layout.addWidget(page_bar)

    def _clear_cards(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _go_page(self, page: int):
        self.current_page = page
        self.refresh()

    def _on_card_click(self, record: dict):
        if record['type'] == 'text' and record.get('content'):
            content = record['content']
            try:
                import pyperclip
                pyperclip.copy(content)
            except Exception:
                pass
            QApplication.instance().clipboard().setText(content)
        elif record['type'] == 'image' and record.get('image_data'):
            img = QImage()
            img.loadFromData(record['image_data'])
            QApplication.instance().clipboard().setImage(img)
