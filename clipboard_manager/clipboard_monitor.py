"""Monitor Windows clipboard for text and image changes."""
from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QClipboard, QImage
from PySide6.QtWidgets import QApplication

from clipboard_manager.database import add_record, cleanup
from clipboard_manager.config import load_config


class ClipboardMonitor(QObject):
    def __init__(self):
        super().__init__()
        self._clipboard = QApplication.instance().clipboard()
        self._last_text = ''
        self._last_image_hash = None

        # Poll clipboard every 500ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_clipboard)
        self._timer.start(500)

    def _check_clipboard(self):
        mime = self._clipboard.mimeData()

        if mime.hasImage():
            img: QImage = mime.imageData()
            if img and not img.isNull():
                ba = img.bits()
                if ba:
                    raw = bytes(ba)
                    hsh = hash(raw)
                    if hsh != self._last_image_hash:
                        self._last_image_hash = hsh
                        from PySide6.QtCore import QByteArray, QBuffer
                        buf = QBuffer()
                        buf.open(QBuffer.ReadWrite)
                        img.save(buf, 'PNG')
                        add_record('image', image_data=buf.data().data())
                        self._cleanup()
            return

        if mime.hasText():
            text = mime.text()
            if text and text != self._last_text:
                self._last_text = text
                add_record('text', content=text)
                self._cleanup()
            return

    def _cleanup(self):
        config = load_config()
        cleanup(config.storage_days, config.max_items)
