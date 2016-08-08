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
- Syllabification done semi-automatically to consider morpheme boundaries and phonotactic constraints (described in publication to follow, notes on splitting of consonant clusters below)
- Stress marking inserted: TODO


#### Notes on splitting of consonant clusters

SPLIT THESE WHEN:

bl	(None, presumably: sub-, compounds)
br	(sub-, compounds)
dr	(None -- don't occur at compound boundaries because of final-devoicing)
dw	(None -- don't occur at compound boundaries because of final-devoicing)
fl	(af-, hoof-, self-, half-, -lik, -loos, compounds)
fr	(af-, hoof, self-, half-, compounds)
gl	(NOTINDICT)
gr	(NOTINDICT)
gw	(NOTINDICT)
kl	(-lik, -loos, compounds)
kr	(compounds)
kw	(None, presumably: compounds)
pl	(-lik, -loos, op-, compounds)
pr	(op-, compounds)
tr	(compounds, uit-, ont-)
tw	(None, presumably: compounds)
vr	(None -- don't occur at compound boundaries because of final-devoicing)
xl	(-lik, compounds)
xr	(compounds)

kn	(always, except when occuring morph-initially)

sk	(compounds, des-, mis-, dus-, eens-, eers-, trans-) (e.g. intra: whiskey, askies, miskien, moskou, muskadel, miniskule, masker)
sp	(mis-, compounds) (e.g. intra: aspirant, hospitaal)
sw	(None, presumably: compounds)
st	(compounds, mis-)
sl	(always, except when occuring morph-initially) (-lik, compounds, -loos, los-, mis-, trans-)
sn	(always, except when occuring morph-initially)
sm	(always, except when occuring morph-initially)

rare:
sf	(always, except when occuring morph-initially) (only sfeer)

skr	(mis-, compounds) (e.g. intra: deskriptiewe, diskresie, diskriminasie)
spl	(compounds, mis-) (e.g. intra: eksplisiet, eksploreer)
str	(compounds, presumably: mis-) (e.g. intra: australië, astrant, administreer, ekstreme)
spr	(always, except when occuring morph-initially) (compounds, presumably: mis-)

C	(compounds, agter-, voor-, wan-, waar-, vol-, ver-, alles-, anders-, an-, -af, -op, -agtig, -of, -om, daar-, -in, her-, hier-, -onder, hoof-, hiper-, in-, on-, onder-, op-, van-, ver-) (often in prep. compounds)

#### List of possible reductions

 - mp.t -> m.t
 - Ci.Ci -> _.Ci
 - 



References
----------

TODO
