# coding=utf-8
import os
import sys
import MeCab
import json

dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')

DEFAULT_STOPTAGS = ['BOS/EOS']

def get_part_of_speech(feature):
    return '-'.join([v for v in feature.split(',')[:4] if v != '*'])

def get_reading(feature):
    return feature.split(',')[7]

def get_base_form(feature):
    return feature.split(',')[6]

def tokenize(sentence, stoptags=[], unk_feature=False):
    stoptags += DEFAULT_STOPTAGS

    options = ["-d{}".format(dicdir), "-r{}".format(rcfile),]

    if unk_feature:
        options.append('--unk-feature 未知語,*,*,*,*,*,*,*,*')

    t = MeCab.Tagger(" ".join(options))
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
            "stat": m.stat,
        }

        if part_of_speech not in stoptags:
            tokens.append(token)
        m = m.next

    return {"tokens": tokens}


if __name__ == '__main__':
    sentence = sys.argv[1]
    stoptags = sys.argv[2].split(',')
    unk_feature = True if sys.argv[3] == 'True' else False
    tokens = tokenize(sentence, stoptags, unk_feature)
    print(json.dumps(tokens, ensure_ascii=False, indent=2))
