import unicodedata

def decompose(string, save_as = ''):
    decomp = []
    for char in string:
        if len(hex(ord(char))[2:]) <= 4:
            HEX = 'U+{:>4}'.format(hex(ord(char))[2:]).replace(' ','0')
        else:
            HEX = hex(ord(char)).replace('0x','U+')
        try:
            NAME = unicodedata.name(char)
        except ValueError:
            NAME = ''
        decomp.append(' '.join([char,HEX,NAME]))
    if save_as:
        with open(save_as, 'w') as f:
            f.write('\n'.join(decomp))
    else:
        print('\n'.join(decomp))
