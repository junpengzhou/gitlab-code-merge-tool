# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

import multiprocessing
import os

bind = "0.0.0.0:5000"

_default_workers = multiprocessing.cpu_count() * 2 + 1

workers = int(os.environ.get("GUNICORN_WORKERS", _default_workers))
worker_class = "gevent"
worker_connections = 1000

timeout = 0
graceful_timeout = 60
keepalive = 5

access_log = "-"
error_log = "-"
loglevel = "info"

preload_app = True
