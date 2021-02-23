# Digital Humanities Utilities

Python 3.6+ package containing various utilities relevant in the field of digital humanities.

```shell
$ pip install dh-utils
```

## Unicode utilities

### Convert Greek beta code to unicode

```pycon
>>> from dh_utils.unicode import beta2uni
>>> u.beta2uni('lo/gos')
'λόγος'
```

This is a wrapper of the CLTK converter. We used this converter to also create inverse:

```pycon
>>> from dh_utils.unicode import uni2beta
>>> uni2beta('λόγος')
'lo/gos'
```

NB: Since [cltk](https://pypi.org/project/cltk/) and its dependency [nltk](https://pypi.org/project/nltk/) are relatively large, cltk is added as an optional dependency. To use the `beta2uni` converter, either install cltk separately using `pip install cltk` or install dh-utils including this optional depency with `pip install dh-utils[betacode]`.

### Decompose a unicode string

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

A basic converter from markdown to TEI has been added. It will convert a markdown file like:

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

using a Python snippet like

```pycon
>>> from dh_utils.tei import md2tei
>>> with open('file.md') as f:
>>>    md = md2tei(f.read())
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

The extension `ToTEI` in turn exists solely of the postprocessor `TEIPostprocessor`. It has priority 0, which usually means that it will run after all other postprocessors have finished. If any other behaviour or prioritization is required, the processor `TEIPostprocessor` can also be directly imported (`from dh_utils.tei import TEIPostprocessor`) and used in a custom [markdown extension](https://python-markdown.github.io/extensions/api/).


### Tag languages

Tag languages in a given string based on its script:

```python
>>> from dh_utils.tei import tag_script
>>> tag_script('A line contaning the hebrew אגוז מלך inline', 'Hebr')
'A line contaning the hebrew <foreign xml:lang="he-Hebr">אגוז מלך</foreign> inline'
```

It is also possible to tag a given language based on its script in a TEI XML document (NB: file will be overwritten!):

```python
>>> from dh_utils.tei import tag_script_from_file
>>> tag_script_from_file('path/to/file.xml', 'Arab')
```

The available scripts are stored in `dh_utils.tei.AVAILABLE_SCRIPTS` and are enumerated below:

```python
>>> from dh_utils.tei import AVAILABLE_SCRIPTS
>>> AVAILABLE_SCRIPTS
['Arab', 'Copt', 'Hebr', 'Latn', 'Cyrl']
```

Default language-script codes are used to tag the scripts (stored in `DEFAULT_LCS`), which can be adjusted using the `language_code` keyword argument:

```python
>>> t.tag_script_from_file('path/to/file.xml', 'Cyrl', language_code = 'ov-Cyrs')
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
>>> from dh_utils.tei import crit_app as ca
>>> data_dir = "path/to/data/textgroup/work"
>>> filename = "textgroup.work.edition-extension.xml"
>>> ca_ext = "appcrit1" # Or any other extension
>>> ca.create(filename, ca_ext, data_dir)
```

If a file contains multiple critical apparati, these can be distinguished using `/listApp[@type]`, e.g.:

```xml
<listApp type="superior">
  <app/>
  <app/>
  ...
</listApp>
<listApp type="inferior">
  <app/>
  <app/>
  ...
</listApp>
```

Using the above snippet will combine these apparati into one file. If these should be conerted to separate files, one can pass an additional argument `app_type` to `ca.create` (e.g., `ca.create(filename, ca_ext, data_dir app_type="superior")`) to convert an apparatus separately.
