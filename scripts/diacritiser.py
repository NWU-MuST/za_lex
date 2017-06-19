#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Train a diacritic restoration model -- training text (UTF-8)
   received from STDIN and model file output on STDOUT.
"""
from __future__ import unicode_literals, division, print_function #Py2

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

import sys
import re
import unicodedata
import pickle
import itertools
import argparse
import codecs
import json

import numpy as np
from sklearn import ensemble, cross_validation

DEBUG=False

DEF_N_TREES = 50
DEF_CONTEXT_N = 5

def ints2onehot(l, N):
    """0 is reserved for None
    """
    v = [0] * N
    for i in l:
        assert i in range(N+1)
        if i > 0:
            v[i-1] = 1
    return v

def map_or_0(e, m):
    try:
        return m[e]
    except KeyError:
        return 0

class Diacritiser(object):
    def diacritise(self, line):
        raise NotImplementedError

    def __call__(self, line):
        return self.diacritise(line)

    
class GraphClassifDiacritiser(Diacritiser):
    """Implement diacritic restoration using local graphemes as features.
    """
    def __init__(self, graphs, vgraphs, tgraphs, diacs, n, vcfeats):
        """Define the valid grapheme features, target graphemes, diacritics
           and window size (_n_ chars each side of the target)

           ALL SHOULD BE IN UNICODE-NFC (except _diacs_ and
           _tgraphs_), graphs should typically include SPACE
        """
        self.graphs = dict((g, i+1) for i, g in enumerate(sorted(set(graphs))))
        assert set(vgraphs).issubset(self.graphs)
        self.vowels = set(vgraphs)
        self.nonvowels = set([g for g in self.graphs if g not in self.vowels])
        
        self.tgraphs = set(tgraphs) #target graphs (which may take diacritics)
        assert self.tgraphs.issubset(self.graphs)
        self.diacs = dict((g, i+1) for i, g in enumerate(sorted(set(diacs))))
        self._diacs = dict([(v, k) for k, v in self.diacs.iteritems()])
        self.n = int(n)
        assert self.n >= 1
        self.vcfeats = bool(vcfeats)
        self.normre = re.compile("[^{}]".format(re.escape("".join(self.graphs))))
        self.diacre = re.compile("[{}]".format(re.escape("".join(self.diacs))))

    def _normline(self, line, strip_diacs=False):
        line = line.lower()
        if strip_diacs:
            line = unicodedata.normalize("NFKD", line)
            line = self.diacre.sub("", line)
        line = unicodedata.normalize("NFKC", line)
        line = self.normre.sub("", line)
        return " ".join(line.split())

    def _target_idxs(self, normline):
        idxs = []
        for t in self.tgraphs:
            start = 0
            while True:
                i = normline.find(t, start)
                if i != -1:
                    idxs.append(i)
                    start = i + 1
                else:
                    break
        idxs.sort()
        return idxs
    
    def _get_diacs(self, i, normline):
        """Will typically pass NFD form in here"""
        diacs = []
        ii = i + 1
        while ii < len(normline):
            u = normline[ii]
            if unicodedata.category(u) == "Mn": #Mark, Nonspacing
                if u in self.diacs:
                    diacs.append(self.diacs[u])
            else:
                break
            ii += 1
        return diacs
    
    def _idx_to_target(self, i, normline):
        #GET DIACRITICS (y):
        return ints2onehot(self._get_diacs(i, normline), len(self.diacs))

    def _idx_to_feat(self, i, normline):
        #GET CONTEXT FEATURE (X):
        lc = list(normline[:i][-self.n:])
        lc = [0] * (self.n - len(lc)) + lc #left pad
        rc = list(normline[i+1:i+1+self.n])
        rc += [0] * (self.n - len(rc)) #right pad
        featvec = []
        featvec += itertools.chain(*[ints2onehot([map_or_0(g, self.graphs)], len(self.graphs)) for g in lc])
        featvec += itertools.chain(*[ints2onehot([map_or_0(g, self.graphs)], len(self.graphs)) for g in rc])
        if self.vcfeats:
            lcrc = lc + rc
            lcrcints = [0] * len(lcrc)
            for k, g in enumerate(lcrc):
                if g != 0:
                    lcrcints[k] = int(g in self.vowels) + 1
            featvec += itertools.chain(*[ints2onehot([k], 2) for k in lcrcints])
        return featvec
    
    def train_preproc(self, lines):
        X = []
        Y = []
        print("Collecting contexts...", file=sys.stderr)
        for line in lines:
            #get Y's
            normline = unicodedata.normalize("NFD", self._normline(line, strip_diacs=False))
            if DEBUG:
                print(normline.encode("utf-8"), file=sys.stderr)
            for i in self._target_idxs(normline):
                Y.append(self._idx_to_target(i, normline))
            #get X's
            normline = self._normline(line, strip_diacs=True)
            if DEBUG:
                print(normline.encode("utf-8"), file=sys.stderr)
            for i in self._target_idxs(normline):
                X.append(self._idx_to_feat(i, normline))
            assert len(Y) == len(X)
        X = np.array(X)
        Y = np.array(Y)
        if Y.shape[1] == 1: Y = Y.ravel()
        if DEBUG:
            #print(X, file=sys.stderr)
            #print(Y, file=sys.stderr)
            print("X shape:", X.shape, file=sys.stderr)
            print("Y shape:", Y.shape, file=sys.stderr)
        return X, Y
        

    def train(self, X, Y, numest):
        """DEMIT: Todo more sophisticated hyperparm selection and class weighting
        """
        print("Training classifier", file=sys.stderr)
        clf = ensemble.RandomForestClassifier(n_estimators=numest)
        self.model = clf.fit(X, Y)
        if DEBUG:
            print(self.model, file=sys.stderr)
        return self

    def cvscore(self, X, Y, numest, folds=10):
        """From: http://scikit-learn.org/0.17/modules/cross_validation.html#cross-validation
        """
        print("Cross-validation...", file=sys.stderr)
        clf = ensemble.RandomForestClassifier(n_estimators=numest)
        scores = cross_validation.cross_val_score(clf, X, Y, cv=folds)
        print("Accuracy: %0.2f (± %0.2f)" % (scores.mean(), scores.std() * 2), file=sys.stderr)

    def diacritise(self, line):
        #Input idxs for mapping back
        templateline = self.diacre.sub("", unicodedata.normalize("NFKD", line))
        if DEBUG:
            print(templateline.encode("utf-8"), file=sys.stderr)
        tmplidxs = self._target_idxs(templateline.lower())
        #get X's
        normline = self._normline(line, strip_diacs=True)
        if DEBUG:
            print(normline.encode("utf-8"), file=sys.stderr)
        normidxs = self._target_idxs(normline)
        assert len(tmplidxs) == len(normidxs)
        X = []
        for i in normidxs:
            X.append(self._idx_to_feat(i, normline))
        X = np.array(X)
        if DEBUG:
            print(X, file=sys.stderr)
        #get Y's
        Y = self.model.predict(X)
        if DEBUG:
            print(Y, file=sys.stderr)
        #add diacritics to line
        for tidx, y in zip(reversed(tmplidxs), reversed(Y)):
            diacs = []
            try:
                for i, e in enumerate(y):
                    if e > 0.0:
                        diacs.append(self._diacs[i+1])
            except TypeError:
                if y == 1:
                    diacs.append(self._diacs[1])
            templateline = templateline[:tidx+1] + "".join(diacs) + templateline[tidx+1:]
        return unicodedata.normalize("NFKC", templateline)
        
        

if __name__ == "__main__":
    import random
    import diacritiser
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('langdescr', metavar='LANGDESCR', type=str, help="Description of graphemes, etc. (json)")
    parser.add_argument('--context', type=int, default=DEF_CONTEXT_N, help="Number of characters of context (each side of focus char)")
    parser.add_argument('--numest', type=int, default=DEF_N_TREES, help="Number of estimators to use (random forest classifier)")
    parser.add_argument('--novcfeats', dest="vcfeats", action="store_false", help="Don't create features based on vowel/non-vowel classes")
    parser.add_argument('--noxval', dest="xval", action="store_false", help="Don't report cross-validation score")
    args = parser.parse_args()
                         
    with codecs.open(args.langdescr, encoding="utf-8") as infh:
        langdescr = json.load(infh)
    #Check that "diacritics" and "targetgraphs" are NFD:
    assert all([unicodedata.category(c) == "Mn" for c in langdescr["diacritics"]])
    assert all([(unicodedata.normalize("NFKD", c) == c) and len(c) == 1 for c in langdescr["targetgraphs"]])

    d = diacritiser.GraphClassifDiacritiser(langdescr["graphs"],
                                            langdescr["vowels"],
                                            langdescr["targetgraphs"],
                                            langdescr["diacritics"],
                                            args.context,
                                            args.vcfeats)
    #slurp and train
    lines = [unicode(line, encoding="utf-8").strip() for line in sys.stdin]
    random.shuffle(lines)
    X, Y = d.train_preproc(lines)
    if args.xval:
        d.cvscore(X, Y, numest=args.numest)
    d.train(X, Y, numest=args.numest)

    print(pickle.dumps(d, protocol=pickle.HIGHEST_PROTOCOL))
