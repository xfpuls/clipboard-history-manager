"""Global hotkey registration using Windows API via ctypes."""
import ctypes
from ctypes import wintypes
from PySide6.QtCore import QAbstractNativeEventFilter, QObject, Signal
from PySide6.QtWidgets import QApplication


# Windows API constants
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

VK_CODES = {
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45, 'F': 0x46, 'G': 0x47,
    'H': 0x48, 'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E,
    'O': 0x4F, 'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54, 'U': 0x55,
    'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59, 'Z': 0x5A,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73, 'F5': 0x74,
    'F6': 0x75, 'F7': 0x76, 'F8': 0x77, 'F9': 0x78, 'F10': 0x79,
    'F11': 0x7A, 'F12': 0x7B,
    'Space': 0x20, 'Tab': 0x09, 'Enter': 0x0D, 'Escape': 0x1B,
}


def parse_hotkey(hotkey_str: str) -> tuple:
    """Parse 'Ctrl+Shift+V' into (modifiers, vk_code)."""
    parts = [p.strip() for p in hotkey_str.split('+')]
    mod = 0
    vk = None
    for p in parts:
        p_upper = p.upper()
        if p_upper == 'CTRL':
            mod |= MOD_CONTROL
        elif p_upper == 'SHIFT':
            mod |= MOD_SHIFT
        elif p_upper == 'ALT':
            mod |= MOD_ALT
        elif p_upper == 'WIN':
            mod |= MOD_WIN
        else:
            vk = VK_CODES.get(p_upper)
    return mod, vk


class HotkeyFilter(QObject, QAbstractNativeEventFilter):
    """Native event filter that receives WM_HOTKEY messages."""

    hotkey_triggered = Signal()

    def __init__(self):
        QObject.__init__(self)
        QAbstractNativeEventFilter.__init__(self)
        self._hotkey_id = 1
        self._registered = False

    def register(self, hotkey_str: str) -> bool:
        self.unregister()
        mod, vk = parse_hotkey(hotkey_str)
        if vk is None:
            return False

        user32 = ctypes.windll.user32
        result = user32.RegisterHotKey(None, self._hotkey_id, mod, vk)
        self._registered = bool(result)
        return self._registered

    def unregister(self):
        if self._registered:
            ctypes.windll.user32.UnregisterHotKey(None, self._hotkey_id)
            self._registered = False

    def nativeEventFilter(self, event_type, message):
        try:
            ptr = int(message)
            msg = ctypes.cast(ptr, ctypes.POINTER(wintypes.MSG))
            if msg.contents.message == WM_HOTKEY and msg.contents.wParam == self._hotkey_id:
                self.hotkey_triggered.emit()
                return True, 0
        except Exception:
            pass
        return False, 0
