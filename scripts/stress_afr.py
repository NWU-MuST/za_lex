#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the Afrikaans rule-based stress assignment implementation,
   largely based on the Masters thesis: "Reëlgebaseerde
   klemtoontoekenning in 'n grafeem-na-foneemstelsel vir Afrikaans" by
   E.W. Mouton.
"""
from __future__ import unicode_literals, division, print_function #Py2

__author__ = "Daniel van Niekerk"
__email__ = "dvn.demitasse@gmail.com"

import sys
import re

from decomp_simple import SyllabDecompounder

def matching_suffix(word, syl, suffs):
    """Check orthography matching and final syl endswith phones (onsets
       may vary because of maximal onset principle and inflectional
       affixes)
    """
    for g, p in suffs.iteritems():
        if word.endswith(g) and syl[-len(p):] == p:
            return True
    return False

def matching_prefix(word, syl, prefs):
    for g, p in prefs.iteritems():
        if word.startswith(g) and syl == p:
            return True
    return False


class LexStresser(object):
    """Contain phoneset with necessary definitions and implement stress
       assignment algorithm and convenience methods
    """
    def __init__(self, phonemeset):
        self.__dict__.update(phonemeset)

        self.vowels = set(ph for ph in self.phones if "vowel" in self.phones[ph])
        self.diphthongs = set(ph for ph in self.phones if "diphthong" in self.phones[ph])
        self.schwa = "ə"
        #Vowel weight (see Mouton (2010:89))
        self.vweight = {"ə": 0, "œ": 1, "æ": 2, "a": 3, "ɔ": 4, "u": 5, "y": 6, "ɛ": 7, "i": 8}
        #Syllable weight by "rime structure" (a combination of Van der Hulst (1984:209) and Combrink & De Stadler (1987: 191))
        #V - vowel
        #C - consonant
        #L - long vowel
        #D - diphthong
        self.rweight = {"V": 0, "L": 1, "VC": 2, "VCC": 3, "VCCC": 3, "LC": 4, "LCC": 5, "LCCC": 5, "D": 6, "DC": 7, "DCC": 8, "DCCC": 8}
        self.superheavy = set(["LC", "DC", "VCC", "VCCC", "LCC", "LCCC", "DCC", "DCCC"])
        #The following is used to determine number of syllables from
        #orthography
        self.graphvowels = ["aai", "aay", "eeu", "ooi", "ooy", "oei",
                            "aa", "ai", "au", "ay", "ee", "ei", "eu", "ie", "oe", "oi", "oo", "ou", "oy", "ui", "uu", "uy",
                            "a", "e", "i", "o", "u", "y",
                            "ä", "é", "è", "ê", "ë", "î", "ï", "ô", "ö", "û", "ü"]
        tmp = "|".join(sorted(self.graphvowels, key=len, reverse=True))
        print(tmp, file=sys.stderr)
        self.graphvowelsre = re.compile(tmp, flags=re.UNICODE)
        #DEMIT: We are conservative in defining affixes here since the
        #matching implementation is naïve. Can revisit/add affixes in
        #brackets if a more sophisticated morphological analysis is
        #done.
        #####
        #unstressed prefixes: these wil be stripped before determining
        #stress, but most in this category contain schwa, so we are
        #conservative as noted above.
        self.us_prefs = {}
        #stressed prefixes: on-, a-, mis-, wan-, aarts-
        self.sc_prefs = {"on": ["ɔ", "n"],
                         "a": ["ɑː"],
                         "mis": ["m", "ə", "s"],
                         "wan": ["v", "a", "n"],
                         "aarts": ["ɑː", "r", "t", "s"]}
        #["ɦ", "æ", "r"] p.30 ?
        #stressed suffixes: -eur, -aal, -eel, -ent, -esk [-is, -tuur]
        self.sc_suffs = {"eur": ["øː", "r"],
                         "aal": ["ɑː", "l"],
                         "eel": ["iə", "l"],
                         "ent": ["ɛ", "n", "t"],
                         "esk": ["ɛ", "s", "k"],
                         "turg": ["t", "œ", "r", "x"],
                         "joen": ["j", "u", "n"]}
        #"stress-drawing" suffixes: -saam, -ig, -lik, -ies, -end, -baar, -loos
        #"Reël 5" also works for: -or, -sie, -naar, -heid, -ing, -skap
        self.sd_suffs = {"saam": ["s", "ɑː", "m"],
                         "ig": ["ə", "x"],
                         "lik": ["l", "ə", "k"],
                         "ies": ["i", "s"],
                         "ent": ["ə", "n", "t"],
                         "baar": ["b", "ɑː", "r"],
                         "loos": ["l", "uə", "s"],
                         "or": ["ɔ", "r"],
                         #"sie": ["s", "i"],
                         "naar": ["n", "ɑː", "r"],
                         "heid": ["ɦ", "əi", "t"],
                         "ing": ["ə", "ŋ"],
                         "skap": ["s", "k", "a", "p"]}
        #unstressed suffixes: these wil be stripped before determining
        #stress, but we are conservative as noted above.
        self.us_suffs = {}
        #DEMIT, evaluate any other affixes seen in the dict not listed
        #above -- think about inflectional affixes.
        
        
    def _num_scwa_in_syls(self, syls):
        c = 0
        for syl in syls:
            if self.schwa in syl:
                c += 1
        return c

    def _get_vowels(self, syls):
        vowels = []
        for syl in syls:
            newsyl = True
            for ph in syl:
                if "vowel" in self.phones[ph] and newsyl:
                    vowels.append(ph)
                    newsyl = False
        return vowels

    def _get_diphthongs(self, syls):
        diphi = set()
        for i, syl in enumerate(syls):
            for ph in syl:
                if ph in self.diphthongs:
                    diphi.add(i)
        return list(sorted(diphi))
            
    def _onset(self, syl):
        onset = []
        for ph in syl:
            if ph in self.vowels:
                return onset
            else:
                onset.append(ph)
        raise Exception("Syllable has no vowel ({})".format("".join(syl)))

    def _rime(self, syl):
        coda = []
        vowel = None
        for ph in syl:
            if ph in self.vowels:
                vowel = ph
            elif vowel is not None:
                coda.append(ph)
        return [vowel] + coda

    def _rem_s(self, rime):
        """Remove trailing "s": (should've ideally been removed by morph process)
        """
        coda = rime[1:]
        if len(coda) > 1 and coda[-1] == "s":
            return rime[:-1]
        return rime

    def _rimestruct(self, rime):
        vowel = rime[0]
        coda = rime[1:]
        if "dur_long" in self.phones[vowel]:
            rimestruct = "L"
        elif "diphthong" in self.phones[vowel]:
            rimestruct = "D"
        else:
            rimestruct = "V"
        return rimestruct + "".join(["C"] * len(coda))

    def _rime_rems_struct(self, syl):
        return self._rimestruct(self._rem_s(self._rime(syl)))

    def _cmp_sylweight(self, r1, r2):
        """Input: Rime of syl 1 and 2
           Returns:
                     1 -- if r1 is heavier than r2
                    -1 -- if r2 is heavier than r1
                     0 -- if r1 == s2
        """
        #1: By "rime structure"
        try:
            if self.rweight[self._rimestruct(r1)] > self.rweight[self._rimestruct(r2)]:
                return 1
            if self.rweight[self._rimestruct(r1)] < self.rweight[self._rimestruct(r2)]:
                return -1
        except KeyError:
            #print("WARNING: Could not determine 'rime weight' (rimes: {} {})".format("".join(r1), "".join(r2)).encode("utf-8"), file=sys.stderr)
            pass
        #2: By "vowel weight"
        try:
            v1 = r1[0]
            v2 = r2[0]
            if self.vweight[v1] > self.vweight[v2]:
                return 1
            if self.vweight[v1] < self.vweight[v2]:
                return -1
        except KeyError:
            #print("WARNING: Could not determine 'vowel weight' difference (rimes: {} {})".format("".join(r1), "".join(r2)).encode("utf-8"), file=sys.stderr)
            pass
        #3: Could not compare or syllables of equal weight
        return 0
            

    def _get_stress_simplex(self, syls):
        #1 - apply simple schwa rules for 2 and 3 syl cases if possible
        if self._num_scwa_in_syls(syls) > 0:
            if len(syls) == 2:
                print("---------- Reël 4".encode("utf-8"), file=sys.stderr, end="")
                if self.schwa in syls[1]:
                    print("a", file=sys.stderr)
                    return [1, 0]
                else:
                    print("b", file=sys.stderr)
                    return [0, 1]
            elif len(syls) == 3:
                if self.schwa in syls[-1]:
                    print("---------- Reël 1".encode("utf-8"), file=sys.stderr, end="")
                    if self._onset(syls[-1]):
                        print("a", file=sys.stderr)
                        return [0, 1, 0]
                    else:
                        print("b", file=sys.stderr)
                        return [1, 0, 0]
                if self.schwa in syls[1]:
                    rimes = [self._rem_s(self._rime(s)) for s in syls]
                    print("---------- Reël 2/3".encode("utf-8"), file=sys.stderr, end="")
                    print("a", file=sys.stderr)
                    sylcmp = self._cmp_sylweight(rimes[0], rimes[2])
                    if sylcmp > 0:
                        return [1, 0, 0]
                    elif sylcmp < 0:
                        return [0, 0, 1]
                    else:
                        if self._rimestruct(rimes[2]).endswith("C"):
                            return [0, 0, 1]
                        else:
                            return [1, 0, 0]
            #DEMIT: this case not discussed by Mouton, but
            #§2.3.3.2 states that "schwa rules" should be
            #exhaustive for 3-syllable words
            rimes = [self._rem_s(self._rime(s)) for s in syls]
            print("---------- not Reël 1-3 (schwa analog of 22/27)".encode("utf-8"), file=sys.stderr)
            ####DEMIT1
            #sylcmp = self._cmp_sylweight(rimes[1], rimes[2])
            #if sylcmp > 0:
            #    return [0, 1, 0]
            #elif sylcmp < 0:
            #    return [0, 0, 1]
            ####DEMIT2
            stresspatt = [0] * len(syls)
            i = 2 #START SCAN AT SECOND LAST SYL FORWARD
            for i in range(2, len(syls)+1):
                if not self.schwa in syls[-i]:
                    stresspatt[-i] = 1
                    return stresspatt
            ####DEMIT3
            #stresspatt = [0] * len(syls)
            #stresspatt[0] = 1
            #return stresspatt
            ####DEMIT4 (3/4 may work better if compounds slip through)
            #for i in range(len(syls)):
            #    if not self.schwa in syls[i]:
            #        stresspatt = [0] * len(syls)
            #        stresspatt[i] = 1
            #        return stresspatt

        #2 - apply simplex rules
        if len(syls) == 2:
            vowels = self._get_vowels(syls)
            if len(self.diphthongs.intersection(vowels)) == 1:
                print("---------- Reël 10".encode("utf-8"), file=sys.stderr)
                if vowels[0] in self.diphthongs:
                    return [1, 0]
                else:
                    return [0, 1]
            rimestructs = [self._rime_rems_struct(s) for s in syls]
            if rimestructs[1] in self.superheavy:
                print("---------- Reël 11".encode("utf-8"), file=sys.stderr)
                return [0, 1]
            else:
                print("---------- Reël 12-16".encode("utf-8"), file=sys.stderr)
                return [1, 0]
        if len(syls) == 3:
            stresspatt = [0] * 3
            diphthongs = self._get_diphthongs(syls)
            if diphthongs:
                print("---------- Reël 17".encode("utf-8"), file=sys.stderr)
                stresspatt[diphthongs[0]] = 1
                return stresspatt
            rimestructs = [self._rime_rems_struct(s) for s in syls]
            if rimestructs[-1] in self.superheavy:
                print("---------- Reël 18".encode("utf-8"), file=sys.stderr)
                stresspatt[-1] = 1
                return stresspatt
            if rimestructs[-2:] == ["V", "VC"]:
                print("---------- Reël 19/21".encode("utf-8"), file=sys.stderr)
                stresspatt[0] = 1
                return stresspatt
            print("---------- Reël 20/22".encode("utf-8"), file=sys.stderr)
            stresspatt[1] = 1
            return stresspatt
        #Length > 3 syllables
        stresspatt = [0] * len(syls)
        diphthongs = self._get_diphthongs(syls)
        if diphthongs:
            print("---------- Reël 23".encode("utf-8"), file=sys.stderr)
            stresspatt[diphthongs[0]] = 1
            return stresspatt
        rimestructs = [self._rime_rems_struct(s) for s in syls]
        if rimestructs[-1] in self.superheavy:
            print("---------- Reël 24/25".encode("utf-8"), file=sys.stderr)
            stresspatt[-1] = 1
            return stresspatt
        if rimestructs[-2:] == ["V", "VC"]:
            print("---------- Reël 26".encode("utf-8"), file=sys.stderr)
            stresspatt[-3] = 1
            return stresspatt
        print("---------- Reël 27".encode("utf-8"), file=sys.stderr)
        stresspatt[-2] = 1
        return stresspatt

    
    def get_stress_word(self, word, syls):
        """This is not designed to be applied to compound words
           DO DECOMPOUNDING FIRST...
        """
        try:
            assert len(syls) > 0
        except AssertionError:
            print(word.encode("utf-8"), file=sys.stderr)
            raise
        if len(syls) < 2:
            return [0]
        stresspatt = [0] * len(syls)
        
        ###1 - APPLY AFFIX RULES
        ##########
        #Reël 6: Stress-carrying prefixes
        if matching_prefix(word, syls[0], self.sc_prefs):
            print("---------- Reël 6".encode("utf-8"), file=sys.stderr)
            stresspatt[0] = 1
            return stresspatt

        #Reël 7: Stress-carrying suffixes
        if matching_suffix(word, syls[-1], self.sc_suffs):
            print("---------- Reël 7".encode("utf-8"), file=sys.stderr)
            stresspatt[-1] = 1
            return stresspatt

        #Reël 5: Stress-drawing suffixes
        if matching_suffix(word, syls[-1], self.sd_suffs):
            print("---------- Reël 5".encode("utf-8"), file=sys.stderr)
            for i in reversed(range(len(syls)-1)): #DEMIT: This should perhaps be limited...
                #if not self.schwa in syls[i]:
                #DEMIT: skip over these same suffixes?:
                if not self.schwa in syls[i] and not syls[i] in self.sd_suffs.values():
                    stresspatt[i] = 1
                    return stresspatt
            #DEMIT: If all schwa, stress first syllable:
            stresspatt[i] = 1
            return stresspatt

        ###2 - APPLY SIMPLEX RULES
        ##########
        #Reël 8/9: Strip unstressed affixes, if defined, before further
        #processing
        lstrip = 0
        rstrip = 0
        s = syls[:]
        if matching_prefix(word, syls[0], self.us_prefs):
            lstrip = 1
        if matching_suffix(word, syls[-1], self.us_suffs):
            rstrip = 1
        if lstrip:
            s = s[lstrip:]
        if rstrip:
            s = s[:-rstrip]
        if len(s) == 1:
            stresspatt = [0]*lstrip + [1] + [0]*rstrip
        else:
            stresspatt = [0]*lstrip + self._get_stress_simplex(s) + [0]*rstrip
        return stresspatt


class LexStresserDecomp(LexStresser):
    def __init__(self, phonemeset, wordlist):
        LexStresser.__init__(self, phonemeset)
        self.decomp = SyllabDecompounder(wordlist)

    def _decomp(self, word, syls):
        wordparts = self.decomp(word)
        #print("wordparts:", wordparts, file=sys.stderr)
        if len(wordparts) > 1:
            #Now determine expected number of syllables in each wordpart
            #so as to split up syllables accordingly and feed to the
            #simple stress assigner
            nvowels = map(len, map(self.graphvowelsre.findall, wordparts))
            #print(nvowels, file=sys.stderr)
            if len(syls) != sum(nvowels) or 0 in nvowels:
                print("_decomp(): nsyls and ngraphvowels missmatch for {} ({})".format(word, wordparts).encode("utf-8"), file=sys.stderr)
                return [(word, syls)]
            parts = []
            i = 0
            for w, nv in zip(wordparts, nvowels):
                parts.append((w, syls[i:i+nv]))
                i += nv
            return parts
        else:
            return [(word, syls)]
        
    def get_stress_word(self, word, syls):
        parts = self._decomp(word, syls)
        stresspatt = []
        for i, part in enumerate(parts):
            w, s = part
            partpatt = super(LexStresserDecomp, self).get_stress_word(w, s)
            if i > 0:
                partpatt = [e*2 for e in partpatt]
            stresspatt.extend(partpatt)
        return stresspatt
        
        
if __name__ == "__main__":
    import codecs
    import json
    import argparse

    import dictconv
    
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('phonesetfile', metavar='PHONESETFILE', type=str, help="File containing the phoneme set (json utf-8).")
    parser.add_argument('--decomp', metavar='WORDLIST', type=str, default=None, help="Apply decompounding before stress assignment (requires a word list)")
    parser.add_argument('--oformat', metavar='OUTPUTFORMAT', default=dictconv.DEF_OUTFORMAT, help="output format (flat|nested)")
    parser.add_argument('--defstresstone', metavar='DEFSTRESSTONE', default=dictconv.DEFSTRESSTONE, help="default stress/tone")
    args = parser.parse_args()

    #load and instantiate
    with codecs.open(args.phonesetfile, encoding="utf-8") as infh:
        phoneset = json.load(infh)
    if args.decomp is None:
        lexstress = LexStresser(phoneset)
        #print(lexstress)
    else:
        with codecs.open(args.decomp, encoding="utf-8") as infh:
            wordlist = infh.read().split()
        lexstress = LexStresserDecomp(phoneset, wordlist)
        #print(lexstress)

    for line in sys.stdin:
        #input format is "flat" separate fields (current stress pattern is ignored/replaced)
        fields = unicode(line.strip(), encoding="utf-8").split()
        word, pos, stresspat, sylspec = fields[:4]
        pronun = fields[4:]

        syls = []
        i = 0
        for syllen in map(int, sylspec):
            syls.append(pronun[i:i+syllen])
            i += syllen
        stresspat = "".join(map(str, lexstress.get_stress_word(word, syls)))

        if args.oformat == "flat":
            print(dictconv.print_flat(word, "None", stresspat, sylspec, pronun, None).encode("utf-8"))
        elif args.oformat == "nested":
            print(dictconv.print_nested(word, "None", stresspat, sylspec, pronun, phoneset, args.defstresstone, None).encode("utf-8"))
        else:
            raise Exception("Invalid output format specified")
