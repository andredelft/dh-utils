# Digital Humanities Utilities

Python 3.6+ package containing various utilities relevant in the field of digital humanities.

```shell
$ pip install dh-utils
```

## Some examples

Tag languages in a given string based on its script:

```pycon
>>> from dh_utils import tei as t
>>> t.tag('A line contaning the hebrew אגוז מלך inline', 'Hebr')
'A line contaning the hebrew <foreign xml:lang="he-Hebr">אגוז מלך</foreign> inline'
```

It is also possible to tag a given language based on its script in a TEI XML document (NB: file will be overwritten!):

```pycon
>>> t.tag_xml('path/to/file.xml', 'Arab')
```

The available scripts are stored in `AVAILABLE_SCRIPTS` and are enumerated below:

```pycon
>>> t.AVAILABLE_SCRIPTS
['Arab', 'Copt', 'Hebr', 'Latn', 'Cyrs']
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
