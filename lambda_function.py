# coding=utf-8
import os
import subprocess
import json
import collections

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
    event = force_utf8(event)
    params = {
        "libdir": libdir,
        "sentence": event.get('sentence', ''),
        "stoptags": event.get('stoptags', '')
    }

    command = """
    LD_LIBRARY_PATH={libdir} \
        python tokenizer.py "{sentence}" "{stoptags}"
    """.format(**params)
    tokens = subprocess.check_output(command, shell=True)

    return json.loads(tokens)
