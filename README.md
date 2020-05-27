# Digital Humanities Utilities

Python 3.6+ package containing various utilities relevant in the field of digital humanities.

```shell
$ pip install dh-utils
```

## TEI utilities

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
['Arab', 'Copt', 'Hebr', 'Latn', 'Cyrl']
```

Default language-script codes are used to tag the scripts (stored in `DEFAULT_LCS`), which can be adjusted using the `language_code` keyword argument:

```pycon
>>> t.tag_xml('path/to/file.xml', 'Cyrl', language_code = 'ov-Cyrs')
```

## Unicode utilities

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
