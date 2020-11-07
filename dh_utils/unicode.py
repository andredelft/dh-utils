import unicodedata
import json
import string
import os
from cltk.corpus.greek.beta_to_unicode import Replacer

FILE_DIR = os.path.split(__file__)[0]
UNI_BETA_DICT = {}
for fname in ['BETA_UNI_LOWER', 'BETA_UNI_UPPER']:
    with open(os.path.join(FILE_DIR, f'{fname}.json')) as f:
        UNI_BETA_DICT.update(json.load(f))

UNI_BETA_TRANS = str.maketrans(UNI_BETA_DICT)

# str.lower(), but only for latin alphabet
LATIN_UPPER_TRANS = str.maketrans(string.ascii_lowercase, string.ascii_uppercase)
LATIN_LOWER_TRANS = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)

def decompose(string, save_as=''):
    decomp = []
    for char in string:
        if len(hex(ord(char))[2:]) <= 4:
            hex = 'U+{:>4}'.format(hex(ord(char))[2:]).replace(' ','0')
        else:
            hex = hex(ord(char)).replace('0x','U+')

        try:
            name = unicodedata.name(char)
        except ValueError:
            name = ''

        decomp.append(' '.join([char, hex, name]))
    if save_as:
        with open(save_as, 'w') as f:
            f.write('\n'.join(decomp))
    else:
        print('\n'.join(decomp))

def beta2uni(text_beta):
    """ Wrapper of the cltk.corpus.greek.beta_to_unicode.Replacer function """
    text_beta = text_beta.translate(LATIN_UPPER_TRANS)
    text_uni = Replacer().beta_code(text_beta.upper())
    return text_uni

def uni2beta(text_uni, normalize=True):
    """ Inverse of beta2uni """
    if normalize:
        text_uni = unicodedata.normalize('NFC',text_uni)
    text_beta = text_uni.translate(UNI_BETA_TRANS)
    text_beta = text_beta.translate(LATIN_LOWER_TRANS)
    return text_beta
