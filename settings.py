import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    from local_settings import *
except ImportError:
    pass
