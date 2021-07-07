import json
import os

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS", "1")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "500")
timeout_str = os.getenv("TIMEOUT", "500")
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = "%s:%s" % (host, port)


cores = int(max_workers_str)
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 1)

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
