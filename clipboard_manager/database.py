"""SQLite database for clipboard history storage."""
import sqlite3
import os
import time
from datetime import datetime, timedelta
from typing import Optional
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.expanduser('~'), '.clipboard_manager')
DB_PATH = os.path.join(DB_DIR, 'history.db')


def _now_ts() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_db() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('text', 'image')),
                content TEXT,
                image_data BLOB,
                timestamp TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON clipboard_history(timestamp DESC)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_pinned ON clipboard_history(pinned)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON clipboard_history(type)')
        conn.commit()


def add_record(ctype: str, content: Optional[str] = None, image_data: Optional[bytes] = None):
    """Add a clipboard record. Deduplicates: if identical to the most recent record, skip."""
    with get_db() as conn:
        # Deduplicate against last record
        cur = conn.execute(
            'SELECT type, content, image_data FROM clipboard_history ORDER BY timestamp DESC LIMIT 1'
        )
        row = cur.fetchone()
        if row:
            if row['type'] == ctype:
                if ctype == 'text' and row['content'] == content:
                    # Same text - update timestamp only
                    conn.execute(
                        'UPDATE clipboard_history SET timestamp = ? WHERE id = (SELECT id FROM clipboard_history ORDER BY timestamp DESC LIMIT 1)',
                        (_now_ts(),)
                    )
                    conn.commit()
                    return
                elif ctype == 'image' and row['image_data'] == image_data:
                    conn.execute(
                        'UPDATE clipboard_history SET timestamp = ? WHERE id = (SELECT id FROM clipboard_history ORDER BY timestamp DESC LIMIT 1)',
                        (_now_ts(),)
                    )
                    conn.commit()
                    return

        ts = _now_ts()
        conn.execute(
            'INSERT INTO clipboard_history (type, content, image_data, timestamp) VALUES (?, ?, ?, ?)',
            (ctype, content, image_data, ts)
        )
        conn.commit()


def get_records(search: str = '', filter_type: str = 'all', page: int = 0,
                per_page: int = 15, include_pinned: bool = True):
    """Get records with optional search, type filter, and pagination."""
    conditions = []
    params = []

    if search:
        conditions.append('content LIKE ?')
        params.append(f'%{search}%')

    if filter_type == 'text':
        conditions.append("type = 'text'")
    elif filter_type == 'image':
        conditions.append("type = 'image'")

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    # Pinned records always come first
    order = 'ORDER BY pinned DESC, timestamp DESC'

    if page > 0:
        offset = (page - 1) * per_page
        limit = f'LIMIT {per_page} OFFSET {offset}'
    else:
        # page=0 returns all items (for main panel quick view)
        limit = ''

    query = f'SELECT * FROM clipboard_history {where} {order} {limit}'
    count_query = f'SELECT COUNT(*) FROM clipboard_history {where}'

    with get_db() as conn:
        records = [dict(r) for r in conn.execute(query, params).fetchall()]
        total = conn.execute(count_query, params).fetchone()[0]
        total_pages = max(1, (total + per_page - 1) // per_page)

    return records, total, total_pages


def get_recent(n: int = 10):
    """Get n most recent records for quick view."""
    with get_db() as conn:
        records = conn.execute(
            'SELECT * FROM clipboard_history ORDER BY pinned DESC, timestamp DESC LIMIT ?',
            (n,)
        ).fetchall()
    return [dict(r) for r in records]


def toggle_pin(record_id: int) -> int:
    """Toggle pin status. Returns new pinned value."""
    with get_db() as conn:
        cur = conn.execute('SELECT pinned FROM clipboard_history WHERE id = ?', (record_id,))
        row = cur.fetchone()
        if row:
            new_val = 0 if row['pinned'] else 1
            conn.execute('UPDATE clipboard_history SET pinned = ? WHERE id = ?', (new_val, record_id))
            conn.commit()
            return new_val
    return 0


def delete_record(record_id: int):
    with get_db() as conn:
        conn.execute('DELETE FROM clipboard_history WHERE id = ?', (record_id,))
        conn.commit()


def cleanup(storage_days: int, max_items: int):
    """Remove expired records and enforce max item limit."""
    with get_db() as conn:
        # Remove by age
        cutoff = (datetime.now() - timedelta(days=storage_days)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            "DELETE FROM clipboard_history WHERE timestamp < ? AND pinned = 0",
            (cutoff,)
        )

        # Remove by count (keep pinned items)
        count = conn.execute('SELECT COUNT(*) FROM clipboard_history').fetchone()[0]
        if count > max_items:
            excess = count - max_items
            conn.execute('''
                DELETE FROM clipboard_history WHERE id IN (
                    SELECT id FROM clipboard_history
                    WHERE pinned = 0
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            ''', (excess,))

        conn.commit()
