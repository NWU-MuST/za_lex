#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" G2P implementation using ICU transliteration rules...
"""
from __future__ import unicode_literals, division, print_function #Py2

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

import re

import icu  # Debian/Ubuntu: apt-get install python-pyicu

class G2P_ICURules(object):
    def __init__(self, phones, rules):
        phones = list(phones)
        phones.sort(key=lambda x:len(x), reverse=True)
        self.phonesre = re.compile("|".join(phones), flags=re.UNICODE)
        self.rules = rules
        self.transliterator = icu.Transliterator.createFromRules("noname", self.rules, icu.UTransDirection.FORWARD)

    def __getstate__(self):
        return {"phonesre": self.phonesre,
                "rules": self.rules}

    def __setstate__(self, d):
        self.__dict__ = d
        self.transliterator = icu.Transliterator.createFromRules("noname", self.rules, icu.UTransDirection.FORWARD)

    def predict_word(self, word):
        pronun = self.transliterator.transliterate(word)
        return [e.group(0) for e in self.phonesre.finditer(pronun)]


if __name__ == "__main__":
    import sys
    import codecs
    import json
    import argparse

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('phonesetfile', metavar='PHONESETFILE', type=str, help="File containing the phoneme set (json utf-8).")
    parser.add_argument('rulesfile', metavar='RULESFILE', type=str, help="File containing the ICU transliteration rules (txt utf-8).")
    args = parser.parse_args()
        
    #load phones
    with codecs.open(args.phonesetfile, encoding="utf-8") as infh:
        phoneset = json.load(infh)
    phones = list(phoneset["phones"].keys())
    assert not any(["|" in ph for ph in phones])
    #load rules
    with codecs.open(args.rulesfile, encoding="utf-8") as infh:
        rules = infh.read()
    #predict stdin
    g2p = G2P_ICURules(phones, rules)
    for line in sys.stdin:
        word = unicode(line.strip(), encoding="utf-8")
        print("{}\t{}".format(word, " ".join(g2p.predict_word(word))).encode("utf-8"))
