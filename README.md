# Digital Humanities Utilities

Python 3.6+ package containing various utilities relevant in the field of digital humanities.

```shell
$ pip install dh-utils
```

## Some examples

Tag languages in a given string based on its script:

```pycon
>>> from dh_utils import tei as t
>>> t.tag('Hebr', 'A line contaning the following inline hebrew אם שאותם הענינים יצאו חוץ מדעתו text')
'A line contaning the following hebrew <foreign xml:lang="he-Hebr">אם שאותם הענינים יצאו חוץ מדעתו</foreign> text'
```

Decompose any unicode string:

```pycon
>>> from dh_utils import unicode as u
>>> u.decompose('λόγος')
λ U+03bb GREEK SMALL LETTER LAMDA
ο U+03bf GREEK SMALL LETTER OMICRON
́ U+0301 COMBINING ACUTE ACCENT
γ U+03b3 GREEK SMALL LETTER GAMMA
ο U+03bf GREEK SMALL LETTER OMICRON
ς U+03c2 GREEK SMALL LETTER FINAL SIGMA
```
