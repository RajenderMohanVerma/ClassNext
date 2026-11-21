"""Vercel entry point for the ClassNext Flask application."""

import os


database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgresql+psycopg://'):
    os.environ['DATABASE_URL'] = database_url.replace(
        'postgresql+psycopg://',
        'postgresql+psycopg2://',
        1,
    )

from app import create_app

app = create_app()

# Vercel's serverless runtime offers no shell to run init_db.py, so create
# any missing tables on cold start. db.create_all() only creates tables
# that do not exist yet — it never alters or drops existing ones — which
# makes this safe to run on every cold start of a fresh database.
if os.environ.get('VERCEL'):
    try:
        from app.extensions import db

        with app.app_context():
            db.create_all()
    except Exception:
        # If the database is unreachable, let the app's normal error
        # handling (and /healthz) report it instead of failing the import.
        pass
