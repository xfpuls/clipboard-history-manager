"""Diagnostic script - click every card and verify clipboard content."""
import sys
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

from clipboard_manager.database import init_db, get_recent
init_db()

from clipboard_manager.ui.main_panel import MainPanel
panel = MainPanel()

from clipboard_manager.ui.card_widget import CardWidget
import pyperclip

f = open('debug_log.txt', 'w', encoding='utf-8')

count = 0
for i in range(panel.cards_layout.count()):
    item = panel.cards_layout.itemAt(i)
    w = item.widget() if item else None
    if isinstance(w, CardWidget):
        count += 1
        record_content = w.record.get('content', '') or '(empty)'
        record_id = w.record.get('id', -1)

        # Simulate click
        w.mouseReleaseEvent(None)
        app.processEvents()

        # Read clipboard
        result = pyperclip.paste()
        match = (result == record_content)

        f.write(f'Card[{i}] id={record_id} record={record_content[:60]}  pasted={result[:60]}  OK={match}\n')

f.write(f'\nTotal cards: {count}\n')
f.close()
print(f'Done - {count} cards tested. See debug_log.txt')
app.quit()
