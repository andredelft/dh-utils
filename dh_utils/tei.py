import regex

def LanguageNotSupported(Exception):
    pass

RANGE = {
    'Copt': '\u03e2-\u03ef\u2c80-\u2cff\u2e0c\u2e0d'
}
COMBINING = {
    'Copt': '\u0300-\u0361'
}
RE = {
    script: regex.compile(fr'[{RANGE[script]}][\s{RANGE[script]}{COMBINING[script]}]*(?<!\s)')
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
