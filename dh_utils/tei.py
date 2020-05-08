import regex
from lxml import etree
from os import path

def LanguageNotSupported(Exception):
    pass

RANGE = {
    # 'Arab': '',
    'Copt': '\u03e2-\u03ef\u2c80-\u2cff\u2e0c\u2e0d',
    'Hebr': '\u05d0-\u05ff\ufb20-\ufb4f',
    'Latn': 'a-zA-Z0-9\u00c0-\u00ff\u1e00-\u1ef9'
}

COMBINING_PUNCT = {
    'Copt': '\u0300-\u0361',
    'Hebr': '\u0590-\u05cf\ufb1d-\ufb1f',
    'Latn': '.,()!:?'
}

RE = {
    script: regex.compile(fr'[{RANGE[script]}][\s{RANGE[script]}{COMBINING_PUNCT[script]}]*(?<!\s)')
    for script in RANGE.keys()
}

DEFAULT_LCS = {
    # 'Arab': 'ar-Arab',
    'Copt': 'cop-Copt',
    'Hebr': 'he-Hebr',
    'Latn': 'la-Latn'
}

def tag(script, string, language_code = ''):
    if script not in RE.keys():
        raise LanguageNotSupported(
            f'Language {script} not (yet) supported, please use one of: '
            + ', '.join(DEFAULT_LCS.keys())
        )
    if not language_code:
        language_code = DEFAULT_LCS[script]
    return RE[script].sub(f'<foreign xml:lang="{language_code}">\g<0></foreign>', string)

# WIP
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
            new_content = tag(script, new_content, language_code)
        new_xml = etree.fromstring(f'<root>{new_content}</root>')
        for child in new_xml.getchildren():
            if string.istext:
                pass
    with open(fname, 'w') as f:
        f.write(etree.tostring(tree, encoding = 'unicode'))
