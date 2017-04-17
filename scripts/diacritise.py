#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply a diacritic restoration model
"""
from __future__ import unicode_literals, division, print_function #Py2

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

class Diacritiser(object):
    def diacritise(self, line):
        raise NotImplementedError

    def __call__(self, line):
        return self.diacritise(line)

if __name__ == "__main__":
    import sys, argparse, pickle
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('modelfn', metavar='MODELFN', type=str, default=None, help="Load from model file (pickle format)")
    args = parser.parse_args()

    with open(args.modelfn) as infh:
        d = pickle.load(infh)
    
    for line in sys.stdin:
        line = unicode(line, encoding="utf-8").strip()
        try:
            print(d.diacritise(line).encode("utf-8"))
        except Exception as e:
            print("CONVERSION FAILED: '{}'".format(line).encode("utf-8"), file=sys.stderr)
            print(str(e), file=sys.stderr)
