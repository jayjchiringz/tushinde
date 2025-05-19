# app/wsgi.py
from app.main import app
from fastapi.middleware.wsgi import WSGIMiddleware # type: ignore
from fastapi import FastAPI # type: ignore

# Create a wrapper for WSGI
def get_wsgi_app():
    return WSGIMiddleware(app)
