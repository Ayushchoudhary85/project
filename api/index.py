"""
Vercel Serverless WSGI Entry Point for PhishGuard.
Exports the Flask application instance for Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Ensure root directory is on Python path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
