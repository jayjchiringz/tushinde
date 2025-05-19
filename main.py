# main.py — WSGI entrypoint for PythonAnywhere
from fastapi.middleware.wsgi import WSGIMiddleware # type: ignore
from app.main import app as fastapi_app

application = WSGIMiddleware(fastapi_app)
