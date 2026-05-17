"""Clipboard history card widget - direct callback, no custom Qt signals."""
from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFontMetrics
from clipboard_manager.database import toggle_pin, delete_record


TYPE_ICONS = {'text': 'Aa', 'image': 'IMG', 'link': 'URL'}
ICON_BG = {'text': '#E3F2FD', 'image': '#F0F0F0', 'link': '#E8F5E9'}
MAX_LINES = 4


def _detect_type(record: dict) -> str:
    if record['type'] == 'image':
        return 'image'
    content = record.get('content', '') or ''
    if content.startswith(('http://', 'https://', 'www.')):
        return 'link'
    return 'text'


class ContentLabel(QLabel):
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
        bounds = fm.boundingRect(rect.adjusted(0, 0, 0, max_height - rect.height()),
                                 Qt.TextWordWrap, self._full_text)
        if bounds.height() <= max_height + 2:
            self.setText(self._full_text)
            self.setToolTip('')
            self.setFixedHeight(min(bounds.height() + 4, max_height + 4))
        else:
            elided = self._truncate_to_lines(fm, rect.width(), max_height)
            self.setText(elided)
            self.setToolTip(self._full_text)
            self.setFixedHeight(max_height + 4)

    def _truncate_to_lines(self, fm, width: int, max_height: int) -> str:
        text = self._full_text
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


class CardWidget(QPushButton):
    def __init__(self, record: dict, on_click, on_pin_toggled, on_deleted):
        super().__init__()
        self.record = record
        self._on_click = on_click
        self._on_pin_toggled = on_pin_toggled
        self._on_deleted = on_deleted
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFlat(True)
        self._build_ui()

    def _build_ui(self):
        record = self.record
        display_type = _detect_type(record)
        is_pinned = bool(record.get('pinned', 0))
        self.setObjectName('cardPinned' if is_pinned else 'card')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

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
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(icon_lbl, alignment=Qt.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        content_text = record.get('content', '') or ''
        if display_type == 'image':
            content_text = '图片'
        self.content_lbl = ContentLabel(content_text)
        self.content_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        text_layout.addWidget(self.content_lbl)

        time_lbl = QLabel(record.get('timestamp', ''))
        time_lbl.setObjectName('timeLabel')
        time_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        text_layout.addWidget(time_lbl)

        layout.addLayout(text_layout, 1)

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

    def mouseReleaseEvent(self, event):
        """Override: call the click callback directly on mouse release."""
        self._on_click(self.record)
        super().mouseReleaseEvent(event)

    def _toggle_pin(self):
        new_val = toggle_pin(self.record['id'])
        self._on_pin_toggled(self.record['id'], new_val)
        self.record['pinned'] = new_val
        self.setObjectName('cardPinned' if new_val else 'card')
        self.style().unpolish(self)
        self.style().polish(self)

    def _delete(self):
        delete_record(self.record['id'])
        self._on_deleted(self.record['id'])
        self.setParent(None)
        self.deleteLater()
