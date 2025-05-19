# asgi_app.py — expose FastAPI app for external WSGI wrapping
from app.main import app

# ASGI application exposed directly
application = app
