# main.py — ASGI to WSGI bridge for PythonAnywhere (no external libs)
from fastapi import FastAPI # type: ignore
from app.main import app  # Your FastAPI app
from fastapi.middleware.wsgi import WSGIMiddleware  # type: ignore

# Wrap FastAPI with WSGI middleware so PythonAnywhere can run it
application = WSGIMiddleware(app)
