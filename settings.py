import logging

DEBUG = False

LOG_LEVEL = logging.INFO

try:
    from local_settings import *
except ImportError:
    pass
