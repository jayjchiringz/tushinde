# wsgi_fastapi_adapter.py — simple bridge to run FastAPI (ASGI) on WSGI
import asyncio
from typing import Callable
from app.main import app as fastapi_app


def application(environ, start_response):
    """Fake WSGI adapter for ASGI — NOT true async but works for PythonAnywhere fallback testing."""

    body = b"FastAPI does not natively run on WSGI. Please use Uvicorn in production."
    status = "500 Internal Server Error"
    headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(body)))]
    start_response(status, headers)
    yield body
