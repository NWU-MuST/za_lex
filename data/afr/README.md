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
|-- LICENCE.txt
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
 - Current stress markers have been manually verified against the protocol described briefly below.


### List of possibly useful transformations

Here we keep track of dictionary transformations that may be useful in different applications (contexts). Will possibly provide conversion scripts in the future.

```
mp.t -> m.t
Cₓ.Cₓ -> _.Cₓ
```

### Stress features

Stress features have recently been added to the dictionary and should be considered experimental. The idea with these features is to experiment with a protocol/specification that enhances quality and control in text-to-speech (TTS) synthesis systems.

A summary of conventions:

1. Unstressed (`0`), Primary (`1`) and secondary (`2`) stress levels are defined.
2. All monosyllabic words are marked as unstressed.
3. All polysyllabic words have at least one Primary stressed syllable.
4. For application in TTS systems it is assumed here that the primary functions of the lexical stress feature is disambiguation (words with similar pronunciation but different stress patterns) and to clarify word structure, especially in compound words. This leads to conservative specification of stressed syllables with very few words containing more than two stressed syllables. 
5. More than one stressed syllable is only marked in compound words (although not all compounds necessarily have more than one stressed syllable).
6. Words with fewer than 3 syllables only have a single stressed syllable (and more generally, the upper bound on number of stressed syllables is assumed to be `number of syllables / 2`) -- this is related to point (4).
7. Complex stress patterns in compound words are currently not considered, the resulting simplification is that the first stressed syllable is always marked as primary `1` and all subsequent stressed syllables as `2`.
 
The utility/correctness of these conventions will be tested systematically in the context of TTS systems development and is expected to be reported on along with the development process soon.


References
----------

[1] D.R. van Niekerk, "Syllabification for Afrikaans speech synthesis," in Proceedings of the 27th Annual Symposium of the Pattern Recognition Association of South Africa (PRASA), pp 31-36, Stellenbosch, South Africa, December 2016.
