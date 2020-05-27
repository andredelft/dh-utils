import regex
from lxml import etree
from os import path
from xml.sax.saxutils import unescape, escape

class LanguageNotSupported(Exception):
    pass

RANGE = {
    'Arab': '\u0606-\u060b\u060e\u060f\u061c-\u064a\u0660-\u066a'\
            '\u066d-\u066f\u0671-\u06d5\u06de\u06e5\u06e6\u06e9\u06ee-\u06ff',
    'Copt': '\u03e2-\u03ef\u2c80-\u2cff\u2e0c\u2e0d',
    'Hebr': '\u05d0-\u05ff\ufb20-\ufb4f',
    'Latn': 'a-zA-Z0-9\u00c0-\u00ff\u1e00-\u1ef9',
    'Cyrl': '\u0400-\u0482\u048a-\u04ff\ua640-\ua66e\ua67e-\ua69d'
}

COMBINING_PUNCT = {
    'Arab': '\u0600-\u0605\u060c\u060d\u0610-\u061b\u064b-\u065f\u066b\u066c'\
            '\u0670\u06d6-\u06dd\u06df-\u06e4\u06e7\u06e8\u06ea-\u06ed',
    'Copt': '\u0300-\u0361',
    'Hebr': '\u0590-\u05cf\ufb1d-\ufb1f',
    'Latn': '.,\(\)!:?;',
    'Cyrl': '\u0301\u20dd\u0483-\u0489\u2de0-\u2dff\ua66f-\ua67d\ua69e\ua69f'
}

RE_STR = {
    script: fr'[{RANGE[script]}][\s{RANGE[script]}{COMBINING_PUNCT[script]}]*(?<!\s)'
    for script in RANGE.keys()
}

# Language specific additions
RE_STR['Latn'] = '(?<!&#?[a-zA-Z0-9]*)' + RE_STR['Latn'] # Avoid escaped xml chars

RE = {script: regex.compile(RE_STR[script]) for script in RANGE.keys()}

DEFAULT_LCS = {
    'Arab': 'ar-Arab',
    'Copt': 'cop-Copt',
    'Hebr': 'he-Hebr',
    'Latn': 'la-Latn',
    'Cyrl': 'cu-Cyrl'
}

AVAILABLE_SCRIPTS = list(DEFAULT_LCS.keys())

def tag(string, script, language_code = '', escape_xml = True):
    if escape_xml:
        string = escape(string)
    if script not in AVAILABLE_SCRIPTS:
        raise LanguageNotSupported(
            f'Language "{script}" not (yet) supported, please use one of: '
            + ', '.join(AVAILABLE_SCRIPTS)
        )
    if not language_code:
        language_code = DEFAULT_LCS[script]
    return RE[script].sub(
        f'<foreign xml:lang="{language_code}">\g<0></foreign>', string
    )

XML_NS = '{http://www.w3.org/XML/1998/namespace}'

def tag_xml(fname, script, language_code = ''):
    if not language_code:
        language_code = DEFAULT_LCS[script]
    tree = etree.parse(fname)
    root = tree.getroot()
    NS = f'{{{root.nsmap[None]}}}' if None in root.nsmap.keys() else ''
    for string in etree.ETXPath(f'//{NS}body//text()')(root):
        parent = string.getparent()
        new_content = escape(str(string))
        # Check first if first ancestor with xml:lang doesn't already declares
        # the language code to be inserted
        if string.is_text:
            lang_parent = parent.xpath(f'ancestor-or-self::*[@xml:lang][1]')
        elif string.is_tail:
            lang_parent = parent.xpath(f'ancestor::*[@xml:lang][1]')

        if (not lang_parent) or (lang_parent[0].attrib[f'{XML_NS}lang'] != language_code):
            new_content = tag(new_content, script, language_code, escape_xml = False)

        # Create XML tree from tagged content and append to existing tree
        try:
            new_xml_root = etree.fromstring(f'<root>{new_content}</root>')
        except etree.XMLSyntaxError:
            raise Exception(new_content)

        if string.is_text:
            parent.text = new_xml_root.text
            for i,el in enumerate(new_xml_root.getchildren()):
                parent.insert(i, el)
        elif string.is_tail:
            parent.tail = new_xml_root.text
            grandparent = parent.getparent()
            i_parent = grandparent.index(parent)
            for i,el in enumerate(new_xml_root.getchildren()):
                grandparent.insert(i_parent + 1 + i, el)

    with open(fname, 'w', encoding = 'utf-8') as f:
        f.write(etree.tostring(tree, encoding = 'unicode'))
