# Digital Humanities Utilities

Python 3.6+ package containing various utilities relevant in the field of digital humanities.

```shell
$ pip install dh-utils
```

## Unicode utilities

Convert Greek beta code to unicode:

```pycon
>>> from dh_utils import unicode as u
>>> u.beta2uni('lo/gos')
'λόγος'
```

This is a wrapper of the CLTK converter. We used this converter to also create inverse:
```pycon
>>> u.uni2beta('λόγος')
'lo/gos'
```

Decompose any unicode string:

```pycon
>>> u.decompose('λόγος')
λ U+03bb GREEK SMALL LETTER LAMDA
ο U+03bf GREEK SMALL LETTER OMICRON
́ U+0301 COMBINING ACUTE ACCENT
γ U+03b3 GREEK SMALL LETTER GAMMA
ο U+03bf GREEK SMALL LETTER OMICRON
ς U+03c2 GREEK SMALL LETTER FINAL SIGMA
```

## TEI utilities

### Convert markdown to TEI

A basic converter from markdown to TEI has been added. It will convert markdown file like:

```
Some paragraph block

> A blockquote

1. An
2. Ordered
3. List

Another paragraph block with _italics_ and __bold__, and:

* An
* Unordered
* List
```

using a snippet like
```pycon
>>> from dh_utils import tei as t
>>> with open('file.md') as f:
>>>    t.md2tei(f.read())
```

to the following TEI XML:

```xml
<p>Some paragraph block</p>
<quote>
  <p>A blockquote</p>
</quote>
<list rend="numbered">
  <item>An</item>
  <item>Ordered</item>
  <item>List</item>
</list>
<p>Another paragraph block with <hi rend="italic">italics</hi> and <hi rend="bold">bold</hi>, and:</p>
<list rend="bulleted">
  <item>An</item>
  <item>Unordered</item>
  <item>List</item>
</list>
```

The function `md2tei` is syntactic sugar for the markdown extension `ToTEI`, which can be used in combination with other extensions as follows:

```pycon
>>> from markdown import markdown
>>> from dh_utils.tei import ToTEI
>>> markdown('some text', extensions=[ToTEI()]) # Other extensions can be added to this list
```

The extension `ToTEI` in turn exists solely of the postprocessor `TEIPostprocessor`, which converts the . It has priority 0, which in most cases means that it will be ran after all other postprocessors have finished. If any other behaviour or prioritization is required, this processor can also be directly imported and used in a custom [markdown extension](https://python-markdown.github.io/extensions/api/).


### Tag languages

Tag languages in a given string based on its script:

```pycon
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


### Refsdecl generator

To generate refsdecl elements, the generator can be used to create etree xml elements:

```python
from dh_utils.tei import refsdecl_generator

refs_decl = refsdecl_generator.generate_for_file("./path/to/file")
refs_decls = refsdecl_generator.generate_for_path("./path/to/files")
```

It can also be used trough the command line interface:

`python -m dh_utils.tei.refsdecl_generator [--update] [PATH]`

By default, it does not update the file but outputs the refsdecl xml to the terminal. If the `--update` flag is given, the file is updated with the generated refsdecl.

### [MyCapytain](https://github.com/Capitains/MyCapytain)-compatilble critical apparatus

The Python API [MyCapytain](https://github.com/Capitains/MyCapytain) only serves the main text of a CTS structured text version, and does not support stand-off annotation, bibliographies, critical apparati, etc. To overcome the last problem, we have developed a script that generates a separate text version of the critical apparatus that can be served through [MyCapytain](https://github.com/Capitains/MyCapytain). Brill's [Scholarly Editions](https://dh.brill.com) uses these separate text versions, which can be displayed [in parallel](https://dh.brill.com/scholarlyeditions/reader/urn:cts:latinLit:stoa0023.stoa001.amo-lat2:14.1.1-14.1.5?right=amo-appcrit3).

The following snippet creates such a critapp file from `textgroup.work.edition-extension.xml` located in `path/to/data/textgroup/work` and saves it as `textgroup.work.edition-appcrit1.xml`

```python
>>> import crit_app as ca
>>> data_dir = "path/to/data/textgroup/work"
>>> filename = "textgroup.work.edition-extension.xml"
>>> ca_ext = "appcrit1" # Or any other extension
>>> ca.create(filename, ca_ext, data_dir)
```
