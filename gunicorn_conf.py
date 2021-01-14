# gunicorn configuration file
# see: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

import os


prefix = 'PCC'


ENV = os.getenv(f'{prefix}_ENV', 'production')
_is_dev_mode = ENV == 'development'

LOG_LEVEL = os.getenv(f'{prefix}_LOG_LEVEL', None)
if LOG_LEVEL is None:
    LOG_LEVEL = 'debug' if _is_dev_mode else 'info'

TIMEOUT = os.getenv(f'{prefix}_TIMEOUT', 300)

bind = '0.0.0.0:8000'
workers = 4

if ENV == 'development':
    reload = True
    reload_engine = 'auto'
    spew = False
else:
    reload = False
    spew = False

timeout = TIMEOUT  # seconds

# Logging
errorlog = '-'
loglevel = LOG_LEVEL
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
