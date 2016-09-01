#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Convert dictionary formats.
"""
from __future__ import unicode_literals, division, print_function #Py2

import os, sys, codecs, json, argparse, itertools

DEF_INFORMAT = "flat"
DEF_OUTFORMAT = "nested"

SYLBOUNDCHAR = "."
STRESSMARKERS = set("012")
DEFSTRESSTONE = "0"

def vowelidx(syl, phset, word):
    for i in range(len(syl)):
        if "vowel" in phset[syl[i]]:
            return i
    print("WARNING: Syllable does not contain a vowel... {}".format(word), file=sys.stderr)
    return len(syl)

def maybemap(ph, phmap=None):
    if phmap is None or ph in STRESSMARKERS:
        return ph
    else:
        return phmap[ph]

def parse_flat(line):
    fields = unicode(line, encoding="utf-8").split()
    word, pos, stresspat, sylspec = fields[:4]
    assert len(stresspat) == len(sylspec)
    phones = fields[4:]
    return word, pos, stresspat, sylspec, phones

def print_flat(word, pos, stresspat, sylspec, phones, phonemap):
    return " ".join([word, pos, "".join(stresspat), "".join(sylspec), " ".join([maybemap(ph, phonemap) for ph in phones])])


def parse_nested(line, defstresstone):
    fields = unicode(line, encoding="utf-8").split()
    word, pos = fields[:2]
    syms = fields[2:]
    syls = [[]]
    for sym in syms:
        if sym != SYLBOUNDCHAR:
            syls[-1].append(sym)
        else:
            syls.append([])
    stresspat = []
    for i in range(len(syls)):
        stress = STRESSMARKERS.intersection(syls[i])
        assert len(stress) < 2
        if stress:
            stresspat.append(list(stress)[0])
        else:
            stresspat.append(defstresstone)
        syls[i] = [ph for ph in syls[i] if ph not in STRESSMARKERS]
    sylspec = [str(len(syl)) for syl in syls]
    phones = list(itertools.chain(*syls))
    return word, pos, stresspat, sylspec, phones

def print_nested(word, pos, stresspat, sylspec, phones, phset, defstresstone, phonemap):
    i = 0
    syls = []
    for n, stress in zip([int(slen) for slen in sylspec], stresspat):
        syl = phones[i:i+n]
        i += n
        voweli = vowelidx(syl, phset, word)
        if stress != defstresstone:
            syl.insert(voweli+1, stress)
        syls.append(syl)
    return "\t".join([word, pos, " . ".join([" ".join([maybemap(e, phonemap) for e in syl]) for syl in syls])])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('phoneset', metavar='PHSET', type=str, help="phone set (json)")
    parser.add_argument('--iformat', metavar='INPUTFORMAT', default=DEF_INFORMAT, help="input format (flat|nested)")
    parser.add_argument('--oformat', metavar='OUTPUTFORMAT', default=DEF_OUTFORMAT, help="output format (flat|nested)")
    parser.add_argument('--outphonemap', metavar='OUTPHMAP', type=str, help="output phone map (tsv)")
    parser.add_argument('--mapreverse', action='store_true', help="apply phone mapping in reverse.")
    parser.add_argument('--defstresstone', metavar='DEFSTRESSTONE', default=DEFSTRESSTONE, help="default stress/tone")
    args = parser.parse_args()

    phonemap = None
    if args.outphonemap is not None:
        phonemap = {}
        with codecs.open(args.outphonemap, encoding="utf-8") as infh:
            for line in infh:
                a, b = line.split()
                if args.mapreverse:
                    a, b = (b, a)
                phonemap[a] = b

    with codecs.open(args.phoneset, encoding="utf-8") as infh:
        phset = json.load(infh)

    for line in sys.stdin:
        if args.iformat == "flat":
            word, pos, stresspat, sylspec, phones = parse_flat(line)
        elif args.iformat == "nested":
            word, pos, stresspat, sylspec, phones = parse_nested(line, args.defstresstone)
        else:
            raise Exception("Invalid input format specified")
        if args.oformat == "flat":
            print(print_flat(word, pos, stresspat, sylspec, phones, phonemap).encode("utf-8"))
        elif args.oformat == "nested":
            print(print_nested(word, pos, stresspat, sylspec, phones, phset, args.defstresstone, phonemap).encode("utf-8"))
        else:
            raise Exception("Invalid output format specified")
        
        

        
