# coding=utf-8
import os
import sys
import MeCab
import json

dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')

DEFAULT_STOPTAGS = ['BOS/EOS']

def analyze(sentence, stoptags=[]):
    def pos(feature):
        return "-".join([v for v in feature.split(',')[:4] if not v is "*"])

    def reading(feature):
        return feature.split(',')[7]

    def baseform(feature):
        return m.feature.split(',')[6]

    stoptags += DEFAULT_STOPTAGS

    t = MeCab.Tagger("-d{} -r{}".format(dicdir, rcfile))
    m = t.parseToNode(sentence)

    tokens = []
    while m:
        if pos(m.feature) not in stoptags:
            tokens.append({
                "surface": m.surface,
                "feature": m.feature,
                "reading": reading(m.feature),
                "pos": pos(m.feature),
                "baseform": baseform(m.feature),
            })
        m = m.next
    return json.dumps(tokens, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    sentence = sys.argv[1]
    stoptags = sys.argv[2].split(',')
    tokens = analyze(sentence, stoptags)
    print(tokens)
