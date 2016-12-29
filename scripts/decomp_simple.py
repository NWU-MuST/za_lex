#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recursive splitting of words for decompounding
"""
from __future__ import unicode_literals, division, print_function #Py2

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

import itertools

import pywrapfst as wfst # Install OpenFST 1.5.4 or later and build with Python bindings


def is_final(fst, state):
    return fst.final(state) != wfst.Weight.Zero(fst.weight_type())


class Decompounder(object):
    def decompound(self, word):
        raise NotImplementedError

    def __call__(self, word):
        return self.decompound(word)


def label_seq(fst, symtablel, which=1, full=0):
    result = []
    total = 0
    state = fst.start()
    while not is_final(fst, state):
        assert fst.num_arcs(state) == 1
        a = list(fst.arcs(state))[0]
        if which == 0:
            l = a.ilabel
        else:
            l = a.olabel
        result.append(l)
        total += float(a.weight)
        state = a.nextstate
    result = [symtablel[i] for i in result]
    if full:
        return result, total
    else:
        return result

class Tree():
    """ Very simple, used to capture recursive structure...
        Modified from:
           http://stackoverflow.com/questions/2598437/how-to-implement-a-binary-tree-in-python
    """
    def __init__(self, value):
      self.nodes = []
      self.value = value

    def insert(self, value):
        self.nodes.append(Tree(value))
        return self.nodes[-1]

    def nleafnodes(self):
        count = 0
        if not self.nodes:
            count += 1
        else:
            for n in self.nodes:
                count += n.nleafnodes()
        return count

    def getsyms(self):
        syms = set()
        syms.add(self.value)
        for n in self.nodes:
            syms.update(n.getsyms())
        return syms

    def makelattice(self, fst, startstate, symtable, cost, firstword):
        length = self.nleafnodes()
        fst.add_arc(startstate, wfst.Arc(symtable[self.value], symtable[self.value], wfst.Weight(fst.weight_type(), cost(self.value, firstword)), startstate+length))
        offset = 0
        for n in self.nodes:
            n.makelattice(fst, startstate+offset, symtable, cost, firstword=False)
            offset += n.nleafnodes()

    def __str__(self):
        l = []
        for node in self.nodes:
            l.extend(str(node).splitlines())
        lines = [str(self.value)] + ["\t" + line for line in l]
        return "\n".join(lines)

def test_tree():
    my_tree = Tree("BobTonySteven")
    my_tree.insert("Bob")
    my_tree.insert("Tony")
    my_tree.insert("Steven")


class SimpleDecompounder(Decompounder):
    def __init__(self, wordlist):
        self.words = set(wordlist)
        
    def _to_split_or_not(self, splitcand):
        if len(splitcand) == 2: #split proposed?
            if splitcand[0] in self.words or splitcand[1] in self.words:
                w = splitcand
            else:
                w = ["".join(splitcand)]
        else:
            w = splitcand
        return w
        
    def _split(self, word, rootnode):
        center = len(word) / 2.0
        scores = []
        for i in range(len(word)):
            w1, w2 = word[:i], word[i:]
            matches = int(w1 in self.words) + int(w2 in self.words)
            if matches:
                #print(w1, w2, [i, matches, abs(i - center)])
                scores.append([i, matches, abs(i - center)])
        if not scores: #early stop if no good candidates
            return [word]
        scores.sort(key=lambda x:x[2])
        scores.sort(key=lambda x:x[1], reverse=True)
        bestidx = scores[0][0]
        if bestidx == 0:
            return [word]
        else:
            #print("trying:", word[:bestidx], word[bestidx:])
            left = rootnode.insert(word[:bestidx])
            self._split(word[:bestidx], left)
            #print(cand1, len(cand1))
            right = rootnode.insert(word[bestidx:])
            self._split(word[bestidx:], right)

    def wordcost(self, word, firstword):
        if firstword:
            return 0.0
        if word in self.words:
            return -1.0
        return 1.0

    def decompound(self, word):
        tree = Tree(word)
        self._split(word, tree)
        #print(tree)
        nleafnodes = tree.nleafnodes()
        #print("Number of leaf nodes:", nleafnodes)
        symtablel = sorted(tree.getsyms())
        symtable = dict([(s, i) for i, s in enumerate(symtablel)])
        #print("Symbols:")
        #print(symtable)
        fst = wfst.Fst()
        [fst.add_state() for i in range(nleafnodes + 1)]
        fst.set_final(nleafnodes, wfst.Weight.One(fst.weight_type()))
        fst.set_start(0)
        tree.makelattice(fst, 0, symtable, self.wordcost, firstword=True)
        #output fst for debugging
        # fstsymtable = wfst.SymbolTable(b"default")
        # for i, sym in enumerate(symtablel):
        #     fstsymtable.add_symbol(sym.encode("utf-8"), i)
        # fst.set_input_symbols(fstsymtable)
        # fst.set_output_symbols(fstsymtable)
        # fst.write("/tmp/debug.fst")
        best = wfst.shortestpath(fst, nshortest=1)
        wordseq = label_seq(best, symtablel)
        return wordseq
        

def test(wordlistfn, compword):
    import codecs
    with codecs.open(wordlistfn, encoding="utf-8") as infh:
        wordlist = infh.read().split()
    csplitter = SimpleDecompounder(wordlist)
    splitform = csplitter.decompound(compword)
    return splitform
    
if __name__ == "__main__":
    import sys, codecs

    with codecs.open(sys.argv[1], encoding="utf-8") as infh:
        decomp = SimpleDecompounder(infh.read().split())

    for line in sys.stdin:
        word = unicode(line.strip(), encoding="utf-8")
        print("\t".join([word, "-".join(decomp(word))]).encode("utf-8"))
