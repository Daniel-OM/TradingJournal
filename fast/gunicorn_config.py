"""
Configuración de Gunicorn para producción
Uso: gunicorn -c gunicorn_config.py app.main:app
"""

import os
import multiprocessing

# Vinculación
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:3000")

# Workers
workers = os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Timeout
timeout = 120

# Keep-alive
keepalive = 5

# Server mechanics
daemon = False
umask = 0o022
tmp_upload_dir = None

# SSL
keyfile = os.getenv("GUNICORN_KEYFILE", None)
certfile = os.getenv("GUNICORN_CERTFILE", None)

# Process naming
proc_name = "trading-journal-api"

# Server hooks
def on_starting(server):
    """Hook ejecutado cuando el servidor inicia"""
    print(f"Starting Trading Journal API on {bind}")

def on_exit(server):
    """Hook ejecutado cuando el servidor sale"""
    print("Trading Journal API stopped")
