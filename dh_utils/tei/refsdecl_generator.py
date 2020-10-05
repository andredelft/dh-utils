import logging
import os
from contextlib import contextmanager
from copy import copy
from dataclasses import dataclass
from itertools import chain
from pathlib import Path

import argparse
from lxml import etree
from anytree import Node, LevelOrderGroupIter, RenderTree
from lxml.etree import Element, dump, ParseError
from typing import List

TEI_XPATH = "/tei:TEI/"
CTS_VERSION_XPATH = "tei:text/tei:body/tei:div[@type][@n]"
CTS_TEXTPART_XPATHS = ["tei:div[@type][@n]", "tei:l[@n]", "tei:ab/tei:l[@n]"]
NSMAP = {"tei": "http://www.tei-c.org/ns/1.0"}


class RefNode(Node):
    element: Element
    n: str
    type: str = None
    subtype: str = None
    xpath_match: str = None


class TextpartNode(RefNode):
    pass


@dataclass
class TextpartPath:
    segments: List[str]
    type: str


def is_textpart(node):
    return isinstance(node, TextpartNode)


def findall(el, xpath):
    """Find all child elements that match xpath query"""
    return el.findall(xpath, namespaces=NSMAP)


def build_node(element, *, parent=None, node_type=RefNode, xpath_match=None):
    type_ = element.attrib.get("type") or node_type.type
    subtype_ = element.attrib.get("subtype") or node_type.subtype

    return node_type(
        name=f"{type_} ({subtype_})" if subtype_ else type_,
        element=element,
        parent=parent,
        type=type_ or "textpart",
        subtype=subtype_ or "line",
        n=element.attrib.get("n"),
        xpath_match=xpath_match,
    )


def build_ref_tree(el):
    work = build_node(el, parent=None)

    for version_el in findall(el, f"./{CTS_VERSION_XPATH}"):
        version = build_node(version_el, parent=work)
        build_textpart_tree(version_el, parent=version)

    return work


def build_textpart_tree(el, parent):
    for xpath_match, textpart_el in find_textparts(el):
        textpart = build_node(
            element=textpart_el,
            parent=parent,
            node_type=TextpartNode,
            xpath_match=xpath_match,
        )
        build_textpart_tree(textpart_el, parent=textpart)


def find_textparts(el):
    return chain(
        *(
            [(path, element) for element in findall(el, f"./{path}")]
            for path in CTS_TEXTPART_XPATHS
        )
    )


def textpart_levels(tree):
    levels, current_level = [], []

    for group in filter(None, LevelOrderGroupIter(tree, filter_=is_textpart)):
        current_level.append(group[0])
        levels.append(copy(current_level))

    return levels


def textpart_paths(tree):
    for ref in textpart_levels(tree):
        segments, type_ = [], None

        for i, node_ in enumerate(ref, start=1):
            type_ = node_.subtype
            segments.append(node_.xpath_match.replace("[@n]", f"[@n='${i}']"))

        yield TextpartPath(segments=segments, type=type_)


def debug_tree(tree):
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))


def build_refs_decl(tree, path_root):
    element = etree.Element("refsDecl", {"n": "CTS"})

    for path in reversed([path for path in textpart_paths(tree)]):
        attrib = {
            "n": path.type,
            "matchPattern": r"\.".join([r"(\w+)"] * len(path.segments)),
            "replacementPattern": f"#xpath({os.path.join(path_root, *path.segments)})",
        }
        element.append(etree.Element("cRefPattern", attrib))

    return element


def update_refsdecl(tree, refs_decl, path):
    encoding_desc = tree.find("//tei:encodingDesc", NSMAP)
    if encoding_desc is None:
        raise Exception("Missing enveloping element 'encodingDesc'")

    existing_refsdecl = encoding_desc.find("./tei:refsDecl", NSMAP)
    if existing_refsdecl is not None:
        encoding_desc.remove(existing_refsdecl)

    encoding_desc.append(refs_decl)

    with open(path, "wb") as writer:
        tree.write(writer, encoding="utf-8")


@contextmanager
def read_xml(path):
    with open(path, "rb") as reader:
        try:
            root_node = etree.fromstring(reader.read())
            yield etree.ElementTree(root_node)
        except ParseError as e:
            logging.exception(Exception(f"Could not parse: {path}", e))
            yield etree.ElementTree()


def xml_paths(path):
    for subdir, dirs, files in os.walk(path):
        yield from (
            os.path.join(subdir, file) for file in files if file.endswith(".xml")
        )


def is_tei_xml(tree):
    return tree.getroot() is not None and tree.find("//tei:*", NSMAP) is not None


def generate_for_file(path, update):
    with read_xml(path) as tree:
        # filter out all non-tei files
        if not is_tei_xml(tree):
            return

        element = build_refs_decl(
            tree=build_ref_tree(el=tree.getroot()),
            path_root=os.path.join(TEI_XPATH, CTS_VERSION_XPATH),
        )

        if update:
            update_refsdecl(tree, element, path)
            print(f"Succesfully updated {path}")

        return element


def generate_for_path(path, update):
    path_ = Path(path)
    for path_ in ([path_] if path_.is_file() else xml_paths(path_)):
        element = generate_for_file(path_, update)
        if element is not None:
            yield element


def generate(args):
    for refsdecl in generate_for_path(path=args.path, update=args.update):
        if not args.update:
            dump(refsdecl)


def parse_args():
    parser = argparse.ArgumentParser(
        description="A tool to dynamically generate refsDecl definitions for TEI files"
    )
    parser.add_argument("path", help="Path to TEI file")
    parser.add_argument(
        "--update",
        action="store_true",
        help="Updates the file with the newly generated refsDecl",
    )
    return parser.parse_args()


if __name__ == "__main__":
    generate(args=parse_args())
