"""Clipboard history card widget - adaptive height."""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFontMetrics
from clipboard_manager.database import toggle_pin, delete_record


TYPE_ICONS = {'text': 'Aa', 'image': 'IMG', 'link': 'URL'}
ICON_BG = {'text': '#E3F2FD', 'image': '#F0F0F0', 'link': '#E8F5E9'}
MAX_LINES = 4  # Maximum visible lines before ellipsis


def _detect_type(record: dict) -> str:
    if record['type'] == 'image':
        return 'image'
    content = record.get('content', '') or ''
    if content.startswith(('http://', 'https://', 'www.')):
        return 'link'
    return 'text'


class ContentLabel(QLabel):
    """Multi-line label that elides after MAX_LINES with proper word wrap."""

    def __init__(self, text: str):
        super().__init__(text)
        self._full_text = text
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet('font-size: 13px; color: #2C3E50;')

    def set_full_text(self, text: str):
        self._full_text = text
        self._update_text()

    def resizeEvent(self, event):
        self._update_text()
        super().resizeEvent(event)

    def _update_text(self):
        if not self._full_text:
            return
        fm = self.fontMetrics()
        rect = self.contentsRect()
        if rect.width() <= 0:
            return
        line_height = fm.lineSpacing()
        max_height = line_height * MAX_LINES

        # Check if text fits within MAX_LINES
        bounds = fm.boundingRect(rect.adjusted(0, 0, 0, max_height - rect.height()),
                                 Qt.TextWordWrap, self._full_text)
        if bounds.height() <= max_height + 2:
            # Text fits — show it all
            self.setText(self._full_text)
            self.setToolTip('')
            self.setFixedHeight(min(bounds.height() + 4, max_height + 4))
        else:
            # Truncate with ellipsis
            elided = self._truncate_to_lines(fm, rect.width(), max_height)
            self.setText(elided)
            self.setToolTip(self._full_text)
            self.setFixedHeight(max_height + 4)

    def _truncate_to_lines(self, fm, width: int, max_height: int) -> str:
        text = self._full_text
        # Binary search for the right cutoff
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            candidate = text[:mid] + '...'
            h = fm.boundingRect(0, 0, width, 0, Qt.TextWordWrap, candidate).height()
            if h <= max_height:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + '...'


class CardWidget(QFrame):
    clicked = Signal(dict)
    pin_toggled = Signal(int, int)
    deleted = Signal(int)

    def __init__(self, record: dict):
        super().__init__()
        self.record = record
        self._build_ui()

    def _build_ui(self):
        record = self.record
        display_type = _detect_type(record)
        is_pinned = bool(record.get('pinned', 0))
        self.setObjectName('cardPinned' if is_pinned else 'card')
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Type icon
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f'background: {ICON_BG.get(display_type, "#E3F2FD")}; '
            f'border-radius: 8px; font-size: 12px; font-weight: bold; '
            f'color: {"#888" if display_type == "image" else "#5C7DA0"};'
        )
        if display_type == 'image' and record.get('image_data'):
            pixmap = QPixmap()
            pixmap.loadFromData(record['image_data'])
            icon_lbl.setPixmap(pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setText(TYPE_ICONS.get(display_type, 'Aa'))
        layout.addWidget(icon_lbl, alignment=Qt.AlignTop)

        # Text content — adaptive height
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        content_text = record.get('content', '') or ''
        if display_type == 'image':
            content_text = '图片'
        self.content_lbl = ContentLabel(content_text)
        text_layout.addWidget(self.content_lbl)

        time_lbl = QLabel(record.get('timestamp', ''))
        time_lbl.setObjectName('timeLabel')
        text_layout.addWidget(time_lbl)

        layout.addLayout(text_layout, 1)

        # Action buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)

        pin_btn = QPushButton('📌')
        pin_btn.setObjectName('pinBtn')
        pin_btn.setFixedSize(24, 24)
        if is_pinned:
            pin_btn.setProperty('pinned', True)
        pin_btn.setToolTip('置顶' if not is_pinned else '取消置顶')
        pin_btn.clicked.connect(self._toggle_pin)
        btn_layout.addWidget(pin_btn)

        del_btn = QPushButton('✕')
        del_btn.setObjectName('deleteBtn')
        del_btn.setFixedSize(24, 24)
        del_btn.setToolTip('删除')
        del_btn.clicked.connect(self._delete)
        btn_layout.addWidget(del_btn)

        layout.addLayout(btn_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.record)
        super().mousePressEvent(event)

    def _toggle_pin(self):
        new_val = toggle_pin(self.record['id'])
        self.pin_toggled.emit(self.record['id'], new_val)
        self.record['pinned'] = new_val
        self.setObjectName('cardPinned' if new_val else 'card')
        self.style().unpolish(self)
        self.style().polish(self)

    def _delete(self):
        delete_record(self.record['id'])
        self.deleted.emit(self.record['id'])
        self.setParent(None)
        self.deleteLater()
