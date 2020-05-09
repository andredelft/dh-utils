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
    'Latn': 'a-zA-Z0-9\u00c0-\u00ff\u1e00-\u1ef9'
}

COMBINING_PUNCT = {
    'Arab': '\u0600-\u0605\u060c\u060d\u0610-\u061b\u064b-\u065f\u066b\u066c'\
            '\u0670\u06d6-\u06dd\u06df-\u06e4\u06e7\u06e8\u06ea-\u06ed',
    'Copt': '\u0300-\u0361',
    'Hebr': '\u0590-\u05cf\ufb1d-\ufb1f',
    'Latn': '.,()!:?;'
}

RE_STR = {
    script: fr'[{RANGE[script]}][\s{RANGE[script]}{COMBINING_PUNCT[script]}]*(?<!\s)'
    for script in RANGE.keys()
}

# Language specific exceptions
# RE_STR['Latn'] = '(?<!&)' + RE_STR['Latn']

RE = {script: regex.compile(RE_STR[script]) for script in RANGE.keys()}

DEFAULT_LCS = {
    'Arab': 'ar-Arab',
    'Copt': 'cop-Copt',
    'Hebr': 'he-Hebr',
    'Latn': 'la-Latn'
}

def tag(script, string, language_code = '', escape_xml = False):
    if escape_xml:
        string = unescape(string)
    if script not in RE.keys():
        raise LanguageNotSupported(
            f'Language "{script}" not (yet) supported, please use one of: '
            + ', '.join(DEFAULT_LCS.keys())
        )
    if not language_code:
        language_code = DEFAULT_LCS[script]
    new_string = RE[script].sub(
        f'<foreign xml:lang="{language_code}">\g<0></foreign>', string
    )
    # Escape everything, then unescape <foreign> tags again
    if escape_xml:
        new_string = escape(new_string)
        new_string = new_string.replace(
            f'&lt;foreign xml:lang="{language_code}"&gt;',
            f'<foreign xml:lang="{language_code}">'
        ).replace(
            '&lt;/foreign&gt;',
            '</foreign>'
        )
    return new_string

XML_NS = '{http://www.w3.org/XML/1998/namespace}'

# Still some WIP

def tag_xml(fname, scripts, language_codes = []):
    if not language_codes:
        language_codes = [DEFAULT_LCS[script] for script in scripts]
    tree = etree.parse(fname)
    root = tree.getroot()
    NS = f'{{{root.nsmap[None]}}}' if None in root.nsmap.keys() else ''
    for string in etree.ETXPath(f'//{NS}body//text()')(root):
        parent = string.getparent()
        new_content = str(string)
        for script, language_code in zip(scripts, language_codes):
            # Check first if first ancestor with xml:lang doesn't already declares
            # the language code to be inserted
            if string.is_text:
                lang_parent = parent.xpath(f'ancestor-or-self::*[@xml:lang][1]')
            elif string.is_tail:
                lang_parent = parent.xpath(f'ancestor::*[@xml:lang][1]')

            if (not lang_parent) or (lang_parent[0].attrib[f'{XML_NS}lang'] != language_code):
                new_content = tag(script, new_content, language_code, escape_xml = True)

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

    with open(fname, 'w') as f:
        f.write(etree.tostring(tree, encoding = 'unicode'))
