#!/usr/env python3

from bs4 import BeautifulSoup


# TODO add dependencies bs4, python-lxml


# TODO
# - find all tags
# if no tags -> all words are tags
# - for tag memorize position
# - change view
# - render

# lines stay on lines
# adjust lines after each iteration -> tags before number corrigate the rest

import re


def lexer(text):
    # Define the regular expressions for each token
    token_specification = [
        ("NUMBER", r"\d+(\.\d+)?"),  # Integer or decimal number
        ("PLUS", r"\+"),  # Plus sign
        ("MINUS", r"-"),  # Minus sign
        ("TIMES", r"\*"),  # Multiplication sign
        ("DIVIDE", r"/"),  # Division sign
        ("LPAREN", r"\("),  # Left parenthesis
        ("RPAREN", r"\)"),  # Right parenthesis
        ("SPACE", r"\s+"),  # Spaces
    ]
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "SPACE":
            continue
        column = mo.start() - line_start
        yield Token(kind, value, line_num, column)
        if kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1


# test the lexer
for token in lexer("1+2*(3-4)/5"):
    print(token)


def get_postions_for_tag(soup, tag_name):
    all_tags = soup.find_all(tag_name)
    if not all_tags:
        return False

    mapping = {}
    text_mod = text
    print(repr(soup))

    for tag in all_tags:
        print(tag)
        line_nr = tag.sourceline
        print(
            "Nr",
            tag.sourceline,
            tag.string,
        )

        tag_str = str(tag)
        index_x_1 = text_mod.index(tag_str)
        index_x_2 = len(tag_str)

        print("unchanged", text_mod.splitlines())
        print("changed", text_mod.splitlines()[line_nr].replace(tag_str, "hello"))

        "\n".join(text_mod.splitlines()[line_nr].replace(tag_str, "hello"))

    print(text_mod)

    # Case that mapping is larger than one:
    # if line_nr in mapping:
    #     length_map = len(mapping[line_nr])
    #     if length_map:
    #         pass
    #


def adjust_other_tag_postions():
    pass


def get_all_tags(soup):
    return [tag.name for tag in soup.find_all() if tag.name not in ("html", "body")]


def remove_p_tags_and_insert_text(html):
    # draft
    soup = BeautifulSoup(html, "html.parser")
    for p in soup.find_all("p"):
        p.replace_with(p.text)
    return str(soup)


text = """
<html>
<head>
  <title>Example website</title>
</head>
<body>
  <div>Hello</div>
  <div>World</div>
  <p>This is a paragraph</p>
  <p>This is another paragraph</p>
</body>
</html>
"""


if __name__ == "__main__":
    text = """
            <a>test1</a>

    <b>test3</b>

    <a>test3</a>
    """

    soup = BeautifulSoup(text, "html.parser", formatter=None)

    # modified_html = remove_p_tags_and_insert_text(text)
    # print(modified_html)

    get_postions_for_tag(soup, "a")
