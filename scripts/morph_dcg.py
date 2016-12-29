#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Loads a simplified form of Definite Clause Grammar (each rule only
   either maps to terminals or nonterminals and no overlap between
   terminal and nonterminal symbols -- see for example:
   `https://github.com/NWU-MuST/bristol-mt-morphology/blob/master/DvN.ZuluDCG.txt`)
   and creates OpenFST grammars to parse and classify words.

   The 'simpleguess' option selects a parse which minimizes the
   open-class portion of the word.
"""
from __future__ import unicode_literals, print_function, division

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

import os, sys
import codecs, pickle
import re
from collections import defaultdict
import tempfile
import pprint

import pywrapfst as wfst # Install OpenFST 1.5.4 or later and build with Python bindings


RULE_RE = re.compile("(?P<head>\w+)\s*\-\-\>\s*(?P<body>.+?)\.")
EPS = "_"

def load_simpledcg(dcg):
    terminals = defaultdict(list)
    nonterminals = defaultdict(list)
    for rule in dcg.splitlines():
        m = RULE_RE.search(rule)
        head, body = m.group("head"), m.group("body")
        if "[" in body:
            syms = list(body.strip("[]"))
            terminals[head].append(syms)
        else:
            syms = re.sub("\s+", "", body).split(",")
            nonterminals[head].append(syms)
    return {"terminals": dict(terminals), "nonterminals": dict(nonterminals)}


def make_symmaps(dcg, graphs, othersyms):
    syms = set(graphs)
    syms.update([e for e in othersyms if e != EPS])
    for k in ["terminals", "nonterminals"]:
        for kk, v in dcg[k].iteritems():
            syms.add(kk)
            for seq in v:
                syms.update(seq)
    itos = dict(zip(range(1, len(syms)+1), sorted(syms)))
    itos[0] = EPS
    stoi = dict((v, k) for k, v in itos.iteritems())
    return itos, stoi


def get_undefsyms(dcg, stoi):
    """Determine which symbols are undefined"""
    defined = set(list(dcg["nonterminals"]) + list(dcg["terminals"]))
    targets = set()
    for k, v in dcg["nonterminals"].iteritems():
        for vv in v:
            targets.update(vv)
    return list(targets.difference(defined))


def make_kleeneplus(s, graphs, stoi):
    """one-or-more-graphs"""
    fst = wfst.Fst()
    start = fst.add_state()
    end = fst.add_state()
    fst.set_start(start)
    fst.set_final(end, wfst.Weight.One(fst.weight_type()))
    for g in graphs:
        fst.add_arc(start, wfst.Arc(stoi[g], stoi[g], wfst.Weight.One(fst.weight_type()), end))
        fst.add_arc(end, wfst.Arc(stoi[g], stoi[g], wfst.Weight.One(fst.weight_type()), end))
    return fst

def make_termfst(s, paths, stoi):
    fst = wfst.Fst()
    start = fst.add_state()
    fst.set_start(start)
    for path in paths:
        a = start
        for g in path:
            b = fst.add_state()
            fst.add_arc(a, wfst.Arc(stoi[g], stoi[g], wfst.Weight.One(fst.weight_type()), b))
            a = b
        fst.set_final(b, wfst.Weight.One(fst.weight_type()))
    fst = wfst.determinize(fst)
    fst.minimize()
    return fst


def make_termfsts(dcg, graphs, stoi):
    """Make fsts mapping terminals to nonterminal symbols"""
    undefsyms = get_undefsyms(dcg, stoi)
    print("UNDEFSYMS:", undefsyms, file=sys.stderr)
    fsts = {}
    for s in undefsyms:
        fsts[s] = make_kleeneplus(s, graphs, stoi)
    for s in dcg["terminals"]:
        fsts[s] = make_termfst(s, dcg["terminals"][s], stoi)        
    return fsts


def save_dot(fst, stoi=None, fn="_fst.dot"):
    fst = fst.copy()
    if stoi is not None:
        st = wfst.SymbolTable()
        for k, v in stoi.iteritems():
            st.add_symbol(k.encode("utf-8"), v)
            fst.set_input_symbols(st)
            fst.set_output_symbols(st)
    fst.draw(fn)
    

def make_input(chars, stoi):
    fst = wfst.Fst()
    s0 = fst.add_state()
    fst.set_start(s0)
    cs = s0
    for c in chars:
        ns = fst.add_state()
        fst.add_arc(cs, wfst.Arc(stoi[c], stoi[c], wfst.Weight.One(fst.weight_type()), ns))
        cs = ns
    fst.set_final(cs, wfst.Weight.One(fst.weight_type()))
    return fst


def make_rtn(s, dcg, stoi, fstcoll):
    fst = wfst.Fst()
    start = fst.add_state()
    fst.set_start(start)
    for path in dcg[s]:
        #print(path, file=sys.stderr)
        a = start
        for ss in path:
            b = fst.add_state()
            if ss in dcg and ss not in fstcoll:
                print("\t\tnew fst: {}".format(ss.upper()), file=sys.stderr)
                make_rtn(ss, dcg, stoi, fstcoll)
            fst.add_arc(a, wfst.Arc(stoi[ss], stoi[ss], wfst.Weight.One(fst.weight_type()), b))
            a = b
        fst.set_final(b, wfst.Weight.One(fst.weight_type()))
    fst = wfst.determinize(fst)
    fst.minimize()
    fstcoll[s] = fst
    return fstcoll


class Morphparse(object):
    """Abstract class just to define the required interface...
    """
    def parse(self, word):
        """Takes a string and returns a list of "parses" where morph labels
        encapsulated by <> precede the string associated with it, for
        example:
             ["<word><noun><iv>u<nst1><npf><n1>m<nst2><nr>numzana",
              "<word><noun><iv_n11>u<nst2><nr>mnumzana",
              ...
             ]
        """
        raise NotImplementedError
        
    def __call__(self, word):
        return self.parse(word)


class Morphparse_DCG(Morphparse):
    def __init__(self, dcg, descr):
        #print("Morphparse_DCG.__init__()", file=sys.stderr)
        #print("dcg[nonterminals]: {}".format(pprint.pformat(dcg["nonterminals"])), file=sys.stderr)
        ###Make symbol tables
        othersyms = set()
        for pos in descr["renamesyms"]:
            othersyms.update([e[1] for e in descr["renamesyms"][pos]])
        self.bounds = descr["bounds"]
        self.itos, self.stoi = make_symmaps(dcg, descr["graphs"], othersyms)

        # #DEBUG DUMP SYMTABLES
        # with codecs.open("tmp/stoi.pickle", "w", encoding="utf-8") as outfh:
        #     pickle.dump(self.stoi, outfh)
        # with codecs.open("tmp/itos.pickle", "w", encoding="utf-8") as outfh:
        #     pickle.dump(self.itos, outfh)

        termfsts = make_termfsts(dcg, descr["graphs"], self.stoi)
        # #DEBUG DUMP FST
        # for k in termfsts:
        #     print("DEBUG dumping:", k, file=sys.stderr)
        #     save_dot(termfsts[k], self.stoi, "tmp/termfst_"+k+".dot")
        #     termfsts[k].write("tmp/termfst_"+k+".fst")
            
        self.fsts = {}
        ###Expand/make non-terminal FSTs for each POS category
        for pos in descr["pos"]:
            print("Making/expanding non-terminal fst for POS:", pos, file=sys.stderr)
            fstcoll = make_rtn(pos, dcg["nonterminals"], self.stoi, {})
            # print("__init__(): fstcoll: {}".format(fstcoll.keys()), file=sys.stderr)
            # for sym in fstcoll:
            #     #DEBUG DUMP FST
            #     save_dot(fstcoll[sym], self.stoi, "tmp/"+pos+"_orig_"+sym+".dot")
            #     fstcoll[sym].write("tmp/"+pos+"_orig_"+sym+".fst")

            #replace non-terminals
            replace_pairs = [(self.stoi[pos], fstcoll.pop(pos))]
            for k, v in fstcoll.iteritems():
                replace_pairs.append((self.stoi[k], v))
            fst = wfst.replace(replace_pairs, call_arc_labeling="both")
            fst.rmepsilon()
            fst = wfst.determinize(fst)
            fst.minimize()
            # #DEBUG DUMP FST
            # save_dot(fst, self.stoi, "tmp/"+pos+"_expanded.dot")
            # fst.write("tmp/"+pos+"_expanded.fst")
            # if True: #DEBUGGING
            #     fst2 = fst.copy()
            #     #rename symbols (simplify) 
            #     if pos in descr["renamesyms"] and descr["renamesyms"][pos]:
            #         labpairs = map(lambda x: (self.stoi[x[0]], self.stoi[x[1]]), descr["renamesyms"][pos])
            #         fst2.relabel_pairs(opairs=labpairs, ipairs=labpairs)
            #     fst2.rmepsilon()
            #     fst2 = wfst.determinize(fst2)
            #     fst2.minimize()            
            #     #DEBUG DUMP FST
            #     save_dot(fst2, self.stoi, "tmp/"+pos+"_expandedsimple.dot")
            #     fst2.write("tmp/"+pos+"_expandedsimple.fst")            

            #replace terminals
            replace_pairs = [(self.stoi[pos], fst)]
            for k, v in termfsts.iteritems():
                replace_pairs.append((self.stoi[k], v))
            fst = wfst.replace(replace_pairs, call_arc_labeling="both")
            fst.rmepsilon()
            fst = wfst.determinize(fst)
            fst.minimize()
            # #DEBUG DUMP FST
            # save_dot(fst, self.stoi, "tmp/"+pos+"_expanded2.dot")
            # fst.write("tmp/"+pos+"_expanded2.fst")

            #rename symbols (simplify) JUST FOR DEBUGGING
            if pos in descr["renamesyms"] and descr["renamesyms"][pos]:
                labpairs = map(lambda x: (self.stoi[x[0]], self.stoi[x[1]]), descr["renamesyms"][pos])
                fst.relabel_pairs(opairs=labpairs, ipairs=labpairs)
            fst.rmepsilon()
            fst = wfst.determinize(fst)
            fst.minimize()            
            # #DEBUG DUMP FST
            # save_dot(fst, self.stoi, "tmp/"+pos+"_prefinal.dot")
            # fst.write("tmp/"+pos+"_prefinal.fst")

            #Convert into transducer:
            #split I/O symbols by convention here: input symbols are single characters:
            #Input syms (relabel outputs to EPS):
            syms = [k for k in self.stoi if len(k) == 1]
            labpairs = map(lambda x: (self.stoi[x], self.stoi[EPS]), syms)
            fst.relabel_pairs(opairs=labpairs)
            #Output syms (relabel inputs to EPS):
            syms = [k for k in self.stoi if len(k) != 1]
            labpairs = map(lambda x: (self.stoi[x], self.stoi[EPS]), syms)
            fst.relabel_pairs(ipairs=labpairs)
            # #DEBUG DUMP FST
            # save_dot(fst, self.stoi, "tmp/"+pos+"_final.dot")
            # fst.write("tmp/"+pos+"_final.fst")
            self.fsts[pos] = fst

    def __getstate__(self):
        fsts = {}
        for pos in self.fsts:
            try:
                fd, path = tempfile.mkstemp()
                self.fsts[pos].write(path)
                with open(path, "rb") as infh:
                    serialisedfst = infh.read()
            finally:
                os.close(fd)
                os.remove(path)
            fsts[pos] = serialisedfst
        d = self.__dict__
        d["fsts"] = fsts
        return d

    def __setstate__(self, d):
        fsts = {}
        fsts = d.pop("fsts")
        for pos in fsts:
            try:
                fd, path = tempfile.mkstemp()
                with open(path, "wb") as outfh:
                    outfh.write(fsts[pos])
                fst = wfst.Fst.read(path)
            finally:
                os.close(fd)
                os.remove(path)
            fsts[pos] = fst
        d["fsts"] = fsts
        self.__dict__ = d

    def parse(self, word, pos=None):
        if pos:
            posl = [pos]
        else:
            posl = list(self.fsts.keys())
        parses = set()
        for pos in posl:
            #print("parse(): trying POS:", pos, file=sys.stderr)
            ifst = make_input(word, self.stoi)
            ofst = wfst.compose(ifst, self.fsts[pos])
            ofstnstates = len(list(ofst.states()))
            if not ofstnstates:
                #print("parse(): no parse for POS:", pos, file=sys.stderr)
                continue
            #print("parse(): parse successful for POS:", pos, file=sys.stderr)
            #save_dot(ofst, self.stoi, "tmp/output.dot")
            paths = []
            dfs_walk(ofst, self.itos, ofst.start(), None, [], paths)
            for path in paths:
                #print(" ".join([e[1] for e in path if e[1]]).encode("utf-8"))
                parses.add("<{}>".format(pos) + path2parse(path))
        parses = [simpbounds(p, self.bounds) for p in sorted(parses)]
        return parses

    def parse_simple(self, word, pos=None):
        re_ins = re.compile("|".join(["<noun>", "<verb>", "<adj>", "<adv>", "<st>"]))
        re_outs = re.compile("|".join(["<cop>", "<loc>", "<pos>", "<prep>", "<pron>", "<ques>", "<rel>", "<pf>", "<sf>"]))
        parses = self.parse(word, pos=pos)
        for i, p in enumerate(parses):
            p = re_ins.sub("{", p)
            p = re_outs.sub("}", p)
            p = p.replace("{}", "")
            p = re.sub("^}", "", p)
            for m in reversed(list(re.finditer("{", p))[1:]):
                p = p[:m.start()] + p[m.end():]
            if "{" in p and not "}" in p:
                p = p + "}"
            if "}" in p and not "{" in p:
                p = p.replace("}", "")
            parses[i] = p
        return list(sorted(set(parses)))
            

def simpbounds(parse, bounds):
    for b in bounds:
        for m in reversed(list(re.finditer("<{}>".format(b), parse))[1:]):
            parse = parse[:m.start()] + parse[m.end():]
    return parse

def path2parse(path):
    parse = []
    for i, o in path:
        if o != EPS:
            parse.append("<{}>".format(o))
        if i != EPS:
            parse.append(i)
    return "".join(parse)
    
def dfs_walk(fst, itos, state, labels, path, fullpaths):
    #print(len(fullpaths), state, file=sys.stderr)
    path = path[:]
    if labels:
        path.append(labels)
    if fst.final(state) != wfst.Weight.Zero(fst.weight_type()): #state is final?
        fullpaths.append(path)
    #print(state, len(list(fst.arcs(state))), file=sys.stderr)
    for arc in fst.arcs(state):
        labs = (itos[arc.ilabel], itos[arc.olabel])
        dfs_walk(fst, itos, arc.nextstate, labs, path, fullpaths)
        

RE_STEM = re.compile("{.+?}")
def simple_nonstemlen(simpleparse):
    return len(RE_STEM.sub("", simpleparse))

        
if __name__ == "__main__":
    import sys, codecs, argparse, pickle, json
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('descrfn', metavar='DESCRFN', type=str, help="JSON file containing a description of how to interpret the DCG file (e.g. graphemes and POS categories etc.)")
    parser.add_argument('dcgfn', metavar='DCGFN', type=str, help="input DCG filename")
    parser.add_argument('--simpleguess', action='store_true', help="output only a single parse analogous to 'stemming' rather than a full morphological information and all possibilities")
    args = parser.parse_args()
    
    with codecs.open(args.descrfn, encoding="utf-8") as infh:
        descr = json.load(infh)
    with codecs.open(args.dcgfn, encoding="utf-8") as infh:
        dcg = load_simpledcg(infh.read())

    morphparse = Morphparse_DCG(dcg, descr)

    for line in sys.stdin:
        word = unicode(line, encoding="utf-8").strip()
        if args.simpleguess:
            parses = morphparse.parse_simple(word)
            parses.sort(key=lambda x: simple_nonstemlen(x), reverse=True)
            parse = parses[0]
            print("{}\t{}".format(word, parse).encode("utf-8"))
        else:
            print("{}\t{}".format(word, " ".join(morphparse(word))).encode("utf-8"))
