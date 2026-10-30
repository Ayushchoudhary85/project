"""
WSGI entry point for PhishGuard on Vercel.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
