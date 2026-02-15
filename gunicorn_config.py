"""
Gunicorn configuration for production deployment of PromptMe-Lite.
Optimized for 200-250 concurrent users across all challenges.

Usage:
    gunicorn -c gunicorn_config.py main:app
"""
import multiprocessing
import os

# Workers - scale based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'  # Use 'gevent' for async if needed
worker_connections = 1000

# Restart workers periodically to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Timeouts (LLM requests can be slow)
timeout = 60  # Request timeout in seconds
graceful_timeout = 30  # Graceful worker shutdown timeout
keepalive = 5

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server socket
bind = '0.0.0.0:5000'
backlog = 2048

# Process naming
proc_name = 'promptme_main'

# Server mechanics
daemon = False  # Run in foreground for Docker/systemd
pidfile = 'logs/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Development/production flag
reload = os.getenv('GUNICORN_RELOAD', 'False').lower() == 'true'

print(f"[GUNICORN] Starting with {workers} workers")
print(f"[GUNICORN] Timeout: {timeout}s")
print(f"[GUNICORN] Bind: {bind}")
