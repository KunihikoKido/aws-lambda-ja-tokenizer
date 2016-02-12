# coding=utf-8
import os
import settings

import logging
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

# preload libmecab
import ctypes
libdir = os.path.join(os.getcwd(), 'local', 'lib')
libmecab = ctypes.cdll.LoadLibrary(os.path.join(libdir, 'libmecab.so'))

import MeCab

# prepare Tagger
dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')
default_tagger = MeCab.Tagger("-d{} -r{}".format(dicdir, rcfile))
unk_tagger = MeCab.Tagger("-d{} -r{} --unk-feature 未知語,*,*,*,*,*,*,*,*".format(dicdir, rcfile))

DEFAULT_STOPTAGS = ['BOS/EOS']

def lambda_handler(event, context):
    sentence = event.get('sentence', '').encode('utf-8')
    stoptags = event.get('stoptags', '').encode('utf-8').split(',') + DEFAULT_STOPTAGS
    unk_feature = event.get('unk_feature', False)

    tokens = []
    tagger = unk_tagger if unk_feature else default_tagger
    node = tagger.parseToNode(sentence)
    while node:
        feature = node.feature + ',*,*'
        part_of_speech = get_part_of_speech(feature)
        reading = get_reading(feature)
        base_form = get_base_form(feature)
        token = {
            "surface": node.surface.decode('utf-8'),
            "feature": node.feature.decode('utf-8'),
            "pos": part_of_speech.decode('utf-8'),
            "reading": reading.decode('utf-8'),
            "baseform": base_form.decode('utf-8'),
            "stat": node.stat,
        }

        if part_of_speech not in stoptags:
            tokens.append(token)
        node = node.next
    return {"tokens": tokens}

def get_part_of_speech(feature):
    return '-'.join([v for v in feature.split(',')[:4] if v != '*'])

def get_reading(feature):
    return feature.split(',')[7]

def get_base_form(feature):
    return feature.split(',')[6]
