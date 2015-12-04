# coding=utf-8
import os
import sys
import MeCab
import json

dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')

DEFAULT_STOPTAGS = ['BOS/EOS']

get_part_of_speech = lambda s: '-'.join([v for v in s.split(',')[:4] if v != '*'])
get_reading = lambda s: s.split(',')[7]
get_base_form = lambda s: s.split(',')[6]

def tokenize(sentence, stoptags=[]):
    stoptags += DEFAULT_STOPTAGS

    option = "-d{dicdir} -r{rcfile}".format(dicdir=dicdir, rcfile=rcfile)
    t = MeCab.Tagger(option)
    m = t.parseToNode(sentence)

    tokens = []
    while m:
        feature = m.feature + ',*,*'
        part_of_speech = get_part_of_speech(feature)
        reading = get_reading(feature)
        base_form = get_base_form(feature)

        token = {
            "surface": m.surface,
            "feature": m.feature,
            "pos": part_of_speech,
            "reading": reading,
            "baseform": base_form,
        }

        if part_of_speech not in stoptags:
            tokens.append(token)
        m = m.next

    return {"tokens": tokens}


if __name__ == '__main__':
    sentence = sys.argv[1]
    stoptags = sys.argv[2].split(',')
    tokens = tokenize(sentence, stoptags)
    print(json.dumps(tokens, ensure_ascii=False))
