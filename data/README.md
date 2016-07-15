Resources
=========

This directory contains the core resources including the pronunciation dictionary and phoneset definitions used by scripts elsewhere.

It also contains the original resource (in `ref`) from which this is derived. The data contained in this directory is considered a *Derivative Work* of the dictionary contained in `ref`.


Basic description of contents and development
---------------------------------------------

### Contents

```
.
|-- graphemeset.txt
|-- LICENCE
|-- phonemeset.ipa-example.tsv
|-- phonemeset.ipa-hts.tsv
|-- phonemeset.ipa-xsampa.tsv
|-- phonemeset.json
|-- pronundict.txt
|-- README.md
`-- ref
    |-- davel10verifying.pdf
    |-- rcrl_apd_20110311
    |   |-- LICENCE
    |   |-- rcrl_apd.1.4.1.txt
    |   `-- README.TXT
    `-- README.md
```

- `pronundict.txt` is the full pronunciation dictionary in the *flat* format and *hts* phoneset representation. Use the scripts in `../scripts` for format and phoneset conversion.


### Development

- Current Afrikaans dictionary (`pronundict.txt`) originates from `./ref/rcrl_apd_20110311/rcrl_apd.1.4.1.txt`
- Small TTS optimisations:
   -- Merging of diphthongs and affricates (TODO: list)
   -- Remove acute accent diacritic (entries) -- see grapheme set in `graphemeset.txt`
- Syllabification done semi-automatically to consider morpheme boundaries and phonotactic constraints (described in publication to follow)
- Stress marking inserted: TODO

References
----------

TODO
