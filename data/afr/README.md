Resources
=========

This directory contains the core resources including the Afrikaans pronunciation dictionary and phoneset definitions used by scripts elsewhere. The dictionary is considered work-in-progress, however it may already be useful ([e.g. in Afrikaans TTS](https://github.com/demitasse/ttslab2_afr_lwazi2_build)). __If used in academic work, please cite [1] or [2].__

It also contains the original resource (in `ref`) from which this is derived. The data contained in this directory is considered a *Derivative Work* of the dictionary contained in `ref`.


Basic description of contents and development
---------------------------------------------

### Contents

```
.
|-- graphemeset.txt
|-- LICENCE.txt
|-- phonememap.ipa-example.tsv
|-- phonememap.ipa-hts.tsv
|-- phonememap.ipa-xsampa.tsv
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

- `pronundict.txt` is the full pronunciation dictionary in the *flat* format and *hts*-friendly phoneset representation. The scripts in `../scripts` can be used for format and phoneset conversion.


### Development

Current state of development:
 - `pronundict.txt` originates from `./ref/rcrl_apd_20110311/rcrl_apd.1.4.1.txt`
 - Adaptations from the source dictionary and inclusion of syllable boundaries is described in the following paper [1].
 - Current stress markers have been manually verified against the protocol described briefly below.

#### Stress features

Stress features have recently been added to the dictionary and should be considered __work-in-progress__. The premise is to experiment with a protocol or specification that enhances quality and control in text-to-speech (TTS) synthesis systems. For a more detailed description of the development process and a formal evaluation in the context of TTS, refer to [2].

A summary of current conventions:

1. Unstressed (`0`), Primary (`1`) and secondary (`2`) stress levels are defined.
2. All monosyllabic words are marked as unstressed.
3. All polysyllabic words have at least one Primary stressed syllable.
4. For application in TTS systems it is assumed here that the primary functions of the lexical stress feature is disambiguation (words with similar pronunciation but different stress patterns) and to clarify word structure, especially in compound words. This leads to conservative specification of stressed syllables with very few words containing more than two stressed syllables. 
5. More than one stressed syllable is only marked in compound words (although not all compounds necessarily have more than one stressed syllable).
6. Words with fewer than 3 syllables only have a single stressed syllable (and more generally, the upper bound on number of stressed syllables is assumed to be `number of syllables / 2`) -- this is related to point (4).
7. Complex stress patterns in compound words are currently not considered, the resulting simplification is that the first stressed syllable is always marked as primary `1` and all subsequent stressed syllables as `2`.
 
As this is considered a __work-in-progress__, it is expected to be refined and extended in future work.

### List of possibly useful (phonetic) transformations

Here we keep track of dictionary transformations that may be useful in different application contexts. Will possibly provide conversion scripts in the future.

```
mp.t -> m.t
Cₓ.Cₓ -> _.Cₓ
```

References
----------

 1. D.R. van Niekerk, "Syllabification for Afrikaans speech synthesis," in _Proceedings of the 27th Annual Symposium of the Pattern Recognition Association of South Africa (PRASA)_, pp. 31-36, Stellenbosch, South Africa, December 2016.
 2. D.R. van Niekerk, "Evaluating acoustic modelling of lexical stress for Afrikaans speech synthesis," in _Proceedings of the 28th Annual Symposium of the Pattern Recognition Association of South Africa (PRASA)_, Bloemfontein, South Africa, December 2017.

```bibtex
@inproceedings{vniekerk2016prasa,
	title = {{Syllabification for Afrikaans speech synthesis}},
	booktitle = {{Proceedings of the Twenty-Seventh Annual Symposium of the Pattern Recognition Association of South Africa (PRASA)}},
	author = {van Niekerk, D. R.},
	address = {Stellenbosch, South Africa},
	month = dec,
	year = {2016},
	pages = {31-36}
}

@inproceedings{vniekerk2017prasa,
	title = {{Evaluating acoustic modelling of lexical stress for Afrikaans speech synthesis}},
	booktitle = {{Proceedings of the Twenty-Eighth Annual Symposium of the Pattern Recognition Association of South Africa (PRASA)}},
	author = {van Niekerk, D. R.},
	address = {Bloemfontein, South Africa},
	month = dec,
	year = {2017}
}
```
