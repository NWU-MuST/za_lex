Resources
=========

This directory contains the core resources including the South African English (SAE) pronunciation dictionary and phoneset definitions used by scripts elsewhere. The dictionary is considered work-in-progress, however it may already be useful ([e.g. in Setswana code-switching TTS](https://github.com/demitasse/ttslab2_tsn_lwazi2_build)). __If used in academic work, please cite [1].__

This dictionary was initially created manually to cover the English subset of words in the TTS corpora described here [1]. The process was informed by previous work on SAE pronunciation for speech technology [2,3].


Basic description of contents and development
---------------------------------------------

### Contents

```
.
|-- COPYRIGHT
|-- graphemeset.txt
|-- phonememap.ipa-example.tsv
|-- phonememap.ipa-hts.tsv
|-- phonememap.ipa-xsampa.tsv
|-- phonemeset.json
|-- pronundict.txt
`-- README.md
```

- `pronundict.txt` is the pronunciation dictionary in the *flat* format and *hts* phoneset representation. Use the scripts in `../scripts` for format and phoneset conversion.


### Development

Current state of development:
 - `pronundict.txt` a minimal dictionary was created manually as described above.

Detailed notes:
 - KIT split [2,3] (avoid reduction where possible)
 - `/@/`-insertion
 - `/z/`-reduction (avoid; leave to speakers)
 - `/i:/`-reduction (avoid; leave to speakers)
 - "ful" and "fully" -> if both possible then `/U/` not `/@/`
 - `/t j/` vs `/tS/` -> `/t j/` followed by `/U/` or `/u:/` stays `/t j .../`
 - `/d j/` vs `/dZ/` -> `/d j/` followed by `/U/` or `/u:/` or `/u@/` stays `/d j .../`
 - "nch" -> `/n S/` -> rather `/n S/` than `/n tS/` at end of syl
 - `/@ r\/` at end -> `/r\/` kept if word end `/@ r\/` and `/3: r\/`; or if followed by a next syl starting with a vowel ("furry" -> `/f 3: . r\ i/`)
 - but not `/@ r\ z/` -> `/@ z/` (is this consistent?)
 - `/3: r\/` only if at word end
 - apostrophe "s" -> voiced gets `/z/`; unvoiced gets `/s/`

Known issues:
 - Only one pronunciation per entry (some homonyms require entries and disambiguation)
 
### Stress features

Stress features have recently been added to the dictionary and should be considered experimental. 


References
----------

 1. D.R. van Niekerk, C. van Heerden, M. Davel, N. Kleynhans, O. Kjartansson, M. Jansche and L. Ha, "__Rapid development of TTS corpora for four South African languages__," in Proceedings of the 18th Annual Conference of the International Speech Communication Association (Interspeech), _forthcoming_, Stockholm, Sweden, August 2017.
```bibtex
@inproceedings{vniekerk2017tts,
	title = {{Rapid development of TTS corpora for four South African languages}},
	booktitle = {{Proceedings of the 18th Annual Conference of the International Speech Communication Association (Interspeech)}},
	author = {van Niekerk, D. R. and van Heerden, C. and Davel, M. and Kleynhans, N. and Kjartansson, O. and Jansche, M. and Ha, L.},
	address = {Stockholm, Sweden},
	month = aug,
	year = {2017},
	pages = {forthcoming}
}
```

 2. O.M. Martirosian, "__Adapting a pronunciation dictionary to Standard South African English for automatic speech recognition__," Thesis, North-West University, 2009.
```bibtex
@phdthesis{martirosian2009sae,
	type = {Thesis},
	title = {{Adapting a pronunciation dictionary to Standard South African English for automatic speech recognition}},
	url = {https://repository.nwu.ac.za:443/handle/10394/4902},
	school = {North-West University},
	author = {Martirosian, Olga Meruzhanovna},
	year = {2009}
}
```

 3. L. Loots, M. Davel, E. Barnard and T. Niesler, "__Comparing manually-developed and data-driven rules for P2P learning__," in Proceedings of the 20th Annual Symposium of the Pattern Recognition Association of South Africa (PRASA), 35-40, Stellenbosch, South Africa, November 2009.
```bibtex
@inproceedings{loots2009p2p,
	title = {{Comparing manually-developed and data-driven rules for P2P learning}},
	booktitle = {{Proceedings of the 20th Annual Symposium of the Pattern Recognition Association of South Africa (PRASA)}},
	author = {Loots, L. and Davel, M. and Barnard, E. and Niesler, T.},
	address = {Stellenbosch, South Africa},
	month = nov,
	year = {2009},
	pages = {35-40}
}
```
