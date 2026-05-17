"""QSS stylesheet for the clipboard manager - light blue theme."""

PRIMARY = '#5B9BD5'
PRIMARY_LIGHT = '#E3F2FD'
BG = '#EBF3FA'
CARD_WHITE = '#FFFFFF'
TEXT_DARK = '#2C3E50'
TEXT_MUTED = '#93B4D0'
BORDER = '#D0DFEF'
BORDER_LIGHT = '#E8F0F8'
PINNED_BORDER = '#B8D4F0'

APP_STYLE = f"""
QWidget {{
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {TEXT_DARK};
}}

QMainWindow {{
    background-color: {BG};
}}

QLineEdit {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
    color: {TEXT_DARK};
}}

QLineEdit:focus {{
    border-color: {PRIMARY};
}}

/* Filter tabs */
QPushButton#filterBtn {{
    background: white;
    color: #5C7DA0;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 5px 14px;
    font-size: 12px;
}}

QPushButton#filterBtn:checked {{
    background: {PRIMARY};
    color: white;
    border: 1px solid {PRIMARY};
}}

/* History button */
QPushButton#historyBtn {{
    background: white;
    color: {PRIMARY};
    border: 1px solid {PRIMARY};
    border-radius: 16px;
    padding: 5px 14px;
    font-size: 12px;
}}

QPushButton#historyBtn:hover {{
    background: {PRIMARY_LIGHT};
}}

/* Settings gear */
QPushButton#settingsBtn {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 8px 12px;
    font-size: 12px;
}}

QPushButton#settingsBtn:hover {{
    background: {PRIMARY_LIGHT};
}}

/* Card */
QPushButton#card {{
    background: white;
    border-radius: 12px;
    border: 1px solid {BORDER_LIGHT};
    text-align: left;
}}

QPushButton#card:hover {{
    background: #FAFBFC;
}}

QPushButton#card:pressed {{
    background: #F0F4F8;
}}

QPushButton#cardPinned {{
    background: white;
    border-radius: 12px;
    border: 1.5px solid {PINNED_BORDER};
    text-align: left;
}}

QPushButton#cardPinned:hover {{
    background: #FAFBFC;
}}

QPushButton#cardPinned:pressed {{
    background: #F0F4F8;
}}

/* Action buttons in cards */
QPushButton#pinBtn, QPushButton#deleteBtn {{
    background: transparent;
    border: none;
    font-size: 14px;
    padding: 2px 4px;
    color: {TEXT_MUTED};
}}

QPushButton#pinBtn:hover, QPushButton#deleteBtn:hover {{
    color: {PRIMARY};
}}

QPushButton#pinBtn[pinned="true"] {{
    color: {PRIMARY};
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #C0D0E0;
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {PRIMARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* Settings switches */
QPushButton#optionBtn {{
    background: white;
    color: #5C7DA0;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 7px 0;
    font-size: 13px;
}}

QPushButton#optionBtn:checked {{
    background: {PRIMARY};
    color: white;
    border: 1px solid {PRIMARY};
}}

/* Back button */
QPushButton#backBtn {{
    background: transparent;
    border: none;
    color: {PRIMARY};
    font-size: 12px;
    padding: 4px 0;
}}

QPushButton#backBtn:hover {{
    color: {TEXT_DARK};
}}

/* Pagination */
QPushButton#pageBtn {{
    background: transparent;
    color: #5C7DA0;
    border: none;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
}}

QPushButton#pageBtn:checked {{
    background: {PRIMARY};
    color: white;
}}

/* Update notification */
QFrame#updateNotify {{
    background: white;
    border-radius: 12px;
    border: 1px solid {BORDER};
}}

QPushButton#updateNowBtn {{
    background: {PRIMARY};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
}}

QPushButton#updateNowBtn:hover {{
    background: #4A8AC4;
}}

QPushButton#updateLaterBtn {{
    background: white;
    color: #999;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
}}

QLabel#timeLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

QLabel#pageTitle {{
    color: {TEXT_DARK};
    font-size: 14px;
    font-weight: bold;
}}

QLabel#sectionTitle {{
    color: {TEXT_DARK};
    font-size: 13px;
    font-weight: bold;
}}

QLabel#hintLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
"""
