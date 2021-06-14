from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
from markdown import markdown

from lxml import etree
import re
from namedentities import unicode_entities

__all__ = ['TEIPostprocessor', 'ToTEI', 'md2tei']


class TEIPostProcessorError(Exception):
    pass


class TEIPostprocessor(Postprocessor):

    def __init__(self, md, indent=False, with_root=False):
        self.indent = indent
        self.with_root = with_root
        Postprocessor.__init__(self, md)

    def _replace_tag(self, old_tag, new_tag, clear_attrib=False, **attribs):
        for el in self.tree.xpath(f'//{old_tag}'):
            el.tag = new_tag

            new_attrib = {}
            for key, value in attribs.items():
                if value.startswith('@'):
                    new_attrib[key] = el.attrib.pop(value[1:], '')
                else:
                    new_attrib[key] = value

            if clear_attrib:
                el.attrib = {}
            el.attrib.update(new_attrib)

    def run(self, text, indent_unit='  '):
        root_tag = 'root'

        # A dirty namespace hack
        text = unicode_entities(text)
        text = text.replace('{http://www.w3.org/XML/1998/namespace}', 'xml:')

        text = f'<{root_tag}>{text}</{root_tag}>'

        try:
            self.tree = etree.fromstring(text)
        except etree.XMLSyntaxError as e:
            lines = text.split('\n')
            error_lineno = e.lineno - 1
            first_lineno = error_lineno - 1 if error_lineno > 0 else 0
            last_lineno = error_lineno + 2 if error_lineno < len(lines) - 1 else len(lines)

            context = []
            for i in range(first_lineno, last_lineno):
                if i == error_lineno:
                    context.append(f' ---> {lines[i]}')
                else:
                    context.append(f'{i+1:>4d}. {lines[i]}')
            context = '\n'.join(context)

            raise TEIPostProcessorError(
                f'XML syntax error encountered from markdown output: {e}\nContext:\n{context}'
            ) from e

        # heads (from old script, not sure if this is actually encountered, AvD)
        for el in self.tree.xpath('//head'):
            el.tag = 'p'
            head = etree.SubElement(el, 'seg')
            head.attrib['type'] = 'head'

            # Move content of over to <seg>
            head.text = el.text
            el.text = ''
            for child in el.getchildren():
                head.append(child)

        # tables
        for table in self.tree.xpath('//table'):
            new_table = etree.Element('table')

            if table.xpath('thead'):
                row = etree.SubElement(new_table, 'row')
                row.attrib['role'] = 'label'
                for cell in table.xpath('thead/tr/th'):
                    cell.tag = 'cell'
                    row.append(cell)

            for table_row in table.xpath('*[not(self::thead)]/tr'):
                row = etree.SubElement(new_table, 'row')
                for cell in table_row.xpath('td'):
                    cell.tag = 'cell'
                    row.append(cell)

            new_table.tail = table.tail

            container = table.getparent()
            container.insert(container.index(table) + 1, new_table)
            del container[container.index(table)]

        self._replace_tag('em', 'hi', rend='italic')
        self._replace_tag('i', 'hi', rend='italic')
        self._replace_tag('strong', 'hi', rend='bold')
        self._replace_tag('b', 'hi', rend='bold')
        self._replace_tag('sup', 'hi', rend='superscript')
        self._replace_tag('sub', 'hi', rend='subscript')
        self._replace_tag('small', 'hi', rend='smallcaps')
        for i in range(1, 7):
            self._replace_tag(f'h{i}', 'head')
        self._replace_tag('br', 'lb')
        self._replace_tag('ol', 'list', rend='numbered')
        self._replace_tag('ul', 'list', rend='bulleted')
        self._replace_tag('li', 'item')
        self._replace_tag('blockquote', 'quote')
        self._replace_tag('a', 'ref', target='@href')
        self._replace_tag('img', 'graphic', n='@alt', url='@src')

        if self.indent:
            etree.indent(self.tree, space=indent_unit)

        new_text = etree.tostring(self.tree, encoding='unicode')

        if not self.with_root:
            # Remove wrapped root element
            new_text = re.sub(rf'^\s*<{root_tag}>|</{root_tag}>\s*$', '', new_text)
            if self.indent:
                new_text = new_text.replace('\n' + indent_unit, '\n')

        return new_text


class ToTEI(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'indent': [False, ''],
            'with_root': [False, '']
        }
        Extension.__init__(self, **kwargs)

    def extendMarkdown(self, md):
        configs = self.getConfigs()
        md.postprocessors.register(TEIPostprocessor(md, configs['indent'], configs['with_root']), 'to_tei', 0)


def md2tei(text):
    return markdown(text, extensions=[ToTEI()])
