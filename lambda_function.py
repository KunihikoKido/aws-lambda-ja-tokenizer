# coding=utf-8
import os
import subprocess
import json

libdir = os.path.join(os.getcwd(), 'local', 'lib')

def lambda_handler(event, context):
    sentence = event.get('sentence', '').encode('utf-8')
    stoptags = event.get('stoptags', '').encode('utf-8')

    print(event)

    cmd = 'LD_LIBRARY_PATH={} python analyzer.py "{}" "{}"'.format(libdir, sentence, stoptags)
    tokens = subprocess.check_output(cmd, shell=True)

    print(tokens)
    return {'tokens': json.loads(tokens)}
