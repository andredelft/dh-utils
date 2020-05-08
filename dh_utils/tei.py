import regex
from lxml import etree
from os import path

def LanguageNotSupported(Exception):
    pass

RANGE = {
    'Copt': '\u03e2-\u03ef\u2c80-\u2cff\u2e0c\u2e0d',
    'Hebr': '\u05d0-\u05ff\ufb20-\ufb4f',
    # 'Latn': 'a-zA-Z0-9\u00c0-\u00ff'
}

COMBINING_PUNCT = {
    'Copt': '\u0300-\u0361',
    'Hebr': '\u0590-\u05cf\ufb1d-\ufb1f',
    # 'Latn': '.,'
}

RE = {
    script: regex.compile(fr'[{RANGE[script]}][\s{RANGE[script]}{COMBINING_PUNCT[script]}]*(?<!\s)')
    for script in RANGE.keys()
}

DEFAULT_LCS = {
    'Copt': 'cop-Copt',
    'Arab': 'ar-Arab',
    'Hebr': 'he-Hebr',
    'Latn': 'la-Latn'
}

def tag(script, string, language_code = ''):
    if script not in RE.keys():
        raise LanguageNotSupported('Language not (yet) supported')
    if not language_code:
        language_code = DEFAULT_LCS[script]
    return RE[script].sub(f'<foreign xml:lang="{language_code}">\g<0></foreign>', string)

# WIP
#
# def tag_xml(fname, scripts = [], language_codes = []):
#     if not language_codes:
#         language_codes = [DEFAULT_LCS[script] for script in scripts]
#     tree = etree.parse(fname)
#     for string in tree.xpath('//text()'):
#         for script, language_code in zip(scripts, language_codes):
#             if string.is_tail:
#                 string.getparent().tail = tag(script, string, language_code)
#             elif string.is_text:
#                 string.getparent().text = tag(script, string, language_code)
#     with open(fname, 'w') as f:
#         f.write(etree.tostring(tree, encoding = 'unicode'))
