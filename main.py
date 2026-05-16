"""Entry point for the Clipboard History Manager."""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clipboard_manager.app import ClipboardApp


def main():
    app = ClipboardApp()
    app.run()


if __name__ == '__main__':
    main()
