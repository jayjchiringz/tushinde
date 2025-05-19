# wsgi_fake.py — fallback WSGI handler for PythonAnywhere
def application(environ, start_response):
    msg = b"""
    FastAPI is ASGI-based and cannot run natively on PythonAnywhere (WSGI-only).
    Please deploy this app on Render.com, Railway.app, or use Flask for full WSGI compatibility.
    """
    status = '500 INTERNAL SERVER ERROR'
    headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(msg)))]
    start_response(status, headers)
    yield msg
