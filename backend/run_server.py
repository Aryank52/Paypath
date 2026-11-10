"""
PayPath Production / Development Server Launcher.
Runs FastAPI ASGI application reliably on 127.0.0.1:8000.
"""

import sys
import os

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

def main():
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()

