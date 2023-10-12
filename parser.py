#!/usr/env python3

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

        result = Position(
            line_nr, tag.sourcepos - 1 - tag_prefix - carry, len(tag.string)
        )
        result.tag = tag
        result.raw_position = Position(line_nr, tag.sourcepos - 1, len(str(tag)))

        carry += carry_new

        yield result


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

        lines[line_nr] = lines[line_nr].replace(str(o_tag), o_tag.string)

        del tag.raw_position, tag.tag

        MAPPING.setdefault(line_nr, []).append(tag)
        # carry = tag.length - len(str(o_tag))

    return "".join(lines)


def tree_transform(text: str) -> str:
    global MAPPING
    assert text and type(text) is str

    MAPPING = {}
    soup = BeautifulSoup(text, "html.parser")

    tags = soup.find_all()
    if not tags:
        print(f"No tags found")
        exit(1)

    return modify_tree(text, tags)


if __name__ == "__main__":
    text = """
            <a>test1</a>__<a>test2</a>
            ---<a>test2</a>

    <b>test3</b>

    <a>test3</a>"""

    new_text = tree_transform(text)
    # print(new_text)

    print(MAPPING)
