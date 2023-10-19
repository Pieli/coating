#!/usr/env python3

import re
from bs4 import BeautifulSoup

MAPPING = {}


class Position:
    def __init__(self, line, column, length):
        self.line = line
        self.column = column
        self.length = length
        self.raw_position = None
        self.tag = None

    def __repr__(self):
        return f"Position({self.line}, {self.column}, {self.length})"


def get_postions_for_tag(tags: iter) -> Position:
    carry, last_line = 0, 0

    for tag in tags:
        line_nr = tag.sourceline - 1

        if line_nr != last_line:
            last_line = line_nr
            carry = 0

        tag_prefix = tag.string.index(tag.string)
        carry_new = len(str(tag)) - len(tag.string)

        result = Position(line_nr, tag.sourcepos - tag_prefix - carry, len(tag.string))
        result.tag = tag
        result.raw_position = Position(line_nr, tag.sourcepos - 1, len(str(tag)))

        carry += carry_new

        yield result


def lexer(text):
    token_specification = [
        ("ELEMENT", r"\S+"),
        ("NEWLINE", r"\n"),
    ]

    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
    line_num = 0
    line_start = 0
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        yield Position(line_num, column, len(value))
        if kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1


def get_all_tags(soup: iter) -> list:
    return [tag.name for tag in soup.find_all() if tag.name not in ("html", "body")]


def modify_tree(text: str, tags: iter) -> str:
    global MAPPING
    assert tags and hasattr(tags, "__iter__")

    lines = text.splitlines(keepends=True)

    for tag in get_postions_for_tag(tags):
        line_nr = tag.raw_position.line
        o_tag = tag.tag

        assert o_tag is not None
        assert str(o_tag) in lines[line_nr]

        lines[line_nr] = lines[line_nr].replace(str(o_tag), o_tag.string, 1)

        del tag.raw_position, tag.tag

        MAPPING.setdefault(line_nr, []).append(tag)

    return "".join(lines)


def tree_transform(text: str) -> str:
    global MAPPING
    assert text and type(text) is str

    MAPPING = {}
    soup = BeautifulSoup(text, "html.parser")

    tags = soup.find_all()
    if not tags:
        for token in lexer(text):
            MAPPING.setdefault(token.line, []).append(token)
        return text

    return modify_tree(text, tags)


if __name__ == "__main__":
    # text = """
    #         <a>test1</a>__<a>test2</a>
    #         ---<a>test2</a>

    # <b>test3</b>

    # <a>test3</a>"""

    text = """
    .rw-r--r--   61 papaya 13 Okt 00:12 requirements.txt
    .rw-r--r--   72 papaya 13 Okt 00:46 testfile
    drwxr-xr-x    - papaya 13 Okt 00:11 venv
    """

    # new_text = tree_transform(text)
    # print(new_text)
    # print(MAPPING)

    for token in lexer(text):
        print(token)
