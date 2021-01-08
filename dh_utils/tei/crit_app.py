import os
from os import path
from lxml import etree
import regex

HERE = path.abspath(path.split(__file__)[0])

re_urn = regex.compile(r'^[^\.]+\.[^\.]+\.[^\-]+-([^\.]+)(?=\.xml$)')

with open(path.join(HERE, 'ca_template.xml')) as f:
    template = f.read()

def parse_urn(fname):
    match = re_urn.search(path.split(fname)[1])
    if match:
        return match.group(), match.group(1)
    else:
        raise Exception(f'Urn {urn} not of correct format')

def to_string(element):
    content = etree.tostring(element, encoding='unicode')
    content = regex.sub(fr'xmlns(?:\:[a-zA-Z]+?)?=".+?"\s*', '', content) # remove all NS
    return content

def recursive_update(dct, passage, value):
    n = passage[0]
    if len(passage) == 1:
        if n in dct.keys():
            dct[n].append(value)
        else:
            dct[n] = [value]
    else:
        if n in dct.keys():
            dct[n] = recursive_update(dct[n], passage[1:], value)
        else:
            dct[n] = recursive_update(dict(), passage[1:], value)
    return dct

def collect_apps(apps, re_passage, NS):
    print(f"{len(apps)} apps found")
    ca_dict = dict()
    not_matched = 0
    for app in apps:
        loc = app.attrib['loc']
        # print(loc)
        match = re_passage.search(loc)
        if match:
            passage = match.groups()
            app_string = to_string(app)
            ca_dict = recursive_update(ca_dict,passage,app_string)
        else:
            not_matched += 1
    print(f"{len(apps) - not_matched} of which loc attribute succesfully interpreted")
    return ca_dict

def format_critapp(ca_dict, levels):
    ca_string = ''
    tag = levels[0]
    for key,value in ca_dict.items():
        tp_type = ' type="textpart"' if tag != 'l' else ''
        if type(value) == list: # len(levels) == 1
            apps_string = '\n'.join(value)
            ca_string += f'<{tag}{tp_type} n="{key}">\n<listApp>\n{apps_string}\n</listApp>\n</{tag}>\n'
        elif type(value) == dict:
            ca_string += f'<{tag}{tp_type} n="{key}">\n{format_critapp(value,levels[1:])}\n</{tag}>\n'
    return ca_string

def create(fname, ca_ext, data_dir='.', lang='', app_type=None):
    urn, extension = parse_urn(fname)
    tree = etree.parse(path.join(data_dir, fname))
    root = tree.getroot()
    NS = f'{{{root.nsmap[None]}}}'
    if not lang:
        lang = etree.ETXPath(f'//{NS}text/{NS}body/{NS}div/@xml:lang')(root)[0]
    print(f"Lanugage: {lang}")

    # find refsDecl
    refsDecl = to_string(etree.ETXPath(f'//{NS}refsDecl')(root)[0])

    # Catch first cRefPattern
    cRef = etree.ETXPath(f'//{NS}refsDecl/{NS}cRefPattern/@replacementPattern')(root)[0]
    levels = regex.findall(r'tei:([a-zA-Z]+)\[@n=[\'"]\$[0-9]+[\'"]\]',cRef)
    print(f"cRefPattern: {', '.join(levels)}")

    # find apps
    passage = r'\.'.join(r'(\w+)' for _ in range(len(levels)))
    urn_wo_ext = regex.sub('-.+?$','',urn)
    print(fr'Searching for {urn_wo_ext}-[\w\-]+?:{passage}')
    re_passage = regex.compile(fr'{urn_wo_ext}-[\w\-]+?:{passage}')
    app_xpath = f'//{NS}app[@loc]'
    if app_type:
        app_xpath = f'//{NS}listApp[@type="{app_type}"]' + app_xpath
    apps = etree.ETXPath(app_xpath)(root)
    ca_dict = collect_apps(apps,re_passage,NS)

    ca_string = format_critapp(ca_dict, levels)

    # Create new file
    new_urn = regex.sub(f'{extension}$', f'{ca_ext}', urn)
    new_fname = regex.sub(f'{extension}(?=.xml$)', f'{ca_ext}', fname)
    content = template.format(content=ca_string, id=new_urn, refsDecl=refsDecl, lang=lang)

    # Indentation
    tree = etree.fromstring(content)
    etree.indent(tree)

    with open(path.join(data_dir, new_fname), 'w') as f:
        f.write(etree.tostring(tree, encoding="unicode"))
