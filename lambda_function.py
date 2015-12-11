# coding=utf-8
import os
import subprocess
import json
import collections

from settings import logger

libdir = os.path.join(os.getcwd(), 'local', 'lib')

def force_utf8(data):
    if isinstance(data, basestring):
        return data.encode('utf-8')
    elif isinstance(data, collections.Mapping):
        return dict(map(force_utf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(force_utf8, data))
    else:
        return data

def lambda_handler(event, context):
    logger.debug(json.dumps(event, ensure_ascii=False, indent=2))

    event = force_utf8(event)
    params = {
        "libdir": libdir,
        "sentence": event.get('sentence', ''),
        "stoptags": event.get('stoptags', ''),
        "unk_feature": event.get('unk_feature', False)
    }

    command = 'LD_LIBRARY_PATH={libdir} python tokenizer.py "{sentence}" "{stoptags}" "{unk_feature}"'.format(**params)
    logger.debug(command)
    tokens = subprocess.check_output(command, shell=True)
    logger.debug(tokens)

    return json.loads(tokens)
