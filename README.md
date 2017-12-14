ZA_LEX: lexical resources for South African languages
=====================================================

This repository contains lexical pronunciation resources and modules for use in text-to-speech (TTS) systems.

Specifically, it was originally set up to track work on updating and enhancing existing resources for the NTTS project funded by the _Department of Arts and Culture_ (DAC) of the Government of South Africa.

The copyright and licence information for scripts in `./scripts/` can be found in `./COPYRIGHT` and `./LICENCE-APACHE`/`./LICENCE-MIT`. This repository also contains data from various sources under different licences in the `./data/*` directories. Copyright and licence information for data and third-party components is contained in each individual sub-directory or source file.

For more information contact: _Daniel van Niekerk_ (http://www.nwu.ac.za/must).

Software dependencies:
----------------------

 - [OpenFST 1.5.0](http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.5.0.tar.gz) or higher with Python bindings.
 - [PyICU](https://pypi.python.org/pypi/PyICU/).

## Description of contents

The top level directory structure is summarised as follows:

```
.
|-- data
|   |-- afr
|   |-- eng
|   |-- sot
|   |-- tsn
|   |-- xho
|   `-- zul
|-- examples
|-- scripts
|-- COPYRIGHT
|-- LICENCE-APACHE
|-- LICENCE-MIT
`-- README.md
```

* The `data` directory contains core language resources organised by language, each associated with its own LICENCE and README.
* The `examples` directory contains some example outputs when running scripts as described below.
* The `scripts` directory contains implementations and UNIX tools for grapheme-to-phoneme (G2P) conversion, syllabification, word decompounding and morphological analysis (some usage examples are given below).

## Usage examples


#### Decompounding

The decompounder `decomp_simple.py` requires a word list and can be run for example on the Afrikaans data as follows:


```bash
cut -d " " -f 1 data/afr/pronundict.txt | scripts/decomp_simple.py examples/afr.words5.txt > examples/afr.decomp.txt
```


#### Morphological analysis

The Zulu morphological analyser can be run as follows (simplified output):

```bash
cut -f 1 data/zul/ref/nchlt_release_20130328/nchlt_isizulu.dict | scripts/morph_dcg.py data/zul/morphrules.descr.json data/zul/morphrules.dcg.txt --simpleguess > examples/zul.morphsimple.txt
```


#### Pronunciation prediction

G2P conversion can be run as follows:

```bash
cut -f 1 data/zul/ref/nchlt_release_20130328/nchlt_isizulu.dict | scripts/g2p_icu.py data/zul/phonemeset.json data/zul/g2p.translit.txt > examples/zul.simple.pronun.txt
cut -f 1 data/tsn/ref/nchlt_release_20130328/nchlt_setswana.dict | scripts/g2p_icu.py data/tsn/phonemeset.json data/tsn/g2p.translit.txt > examples/tsn.simple.pronun.txt
```

The syllabification modules can be run on the resulting pronunciation dictionaries:

```bash
cat examples/zul.simple.pronun.txt | scripts/syl_zul.py data/zul/phonemeset.json | cut -f 1,3 > examples/zul.syll.pronun.txt
cat examples/tsn.simple.pronun.txt | scripts/syl_tsn.py data/tsn/phonemeset.json | cut -f 1,3 > examples/tsn.syll.pronun.txt
```
