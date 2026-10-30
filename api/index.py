"""
Vercel Serverless WSGI Entry Point for PhishGuard.
Exports the Flask application instance for Vercel's Python runtime.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
