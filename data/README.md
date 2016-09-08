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

Current state of development:
 - `pronundict.txt` originates from `./ref/rcrl_apd_20110311/rcrl_apd.1.4.1.txt`
 - Adaptations from the source dictionary and inclusion of syllable boundaries is described in the following paper [1].
 - Current stress markers are experimental, this should be considered work-in-progress.


### List of possibly useful transformations

Here we keep track of dictionary transformations that may be useful in different applications (contexts). Will possibly provide conversion scripts in the future.

```
mp.t -> m.t
Cₓ.Cₓ -> _.Cₓ
```


References
----------

[1] __Forthcoming__
