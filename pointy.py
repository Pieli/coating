import os
import curses
from curses import wrapper

import parser


# Mouse position: run with TERM=xterm-1003
os.environ["TERM"] = "xterm-1003"


# 1. Parse regular expression (begin without)
# 2. apply reg expression and calculate start + stop
# 3. on click/hover loop through hash of line (start, stop, category)


# TODO
# ncurses scroll? -> start with fixed
# draw in different colors

TEXT = """
AAA BBB
ccc
DDDD
"""

OUTPUT = ""


def draw_to_screen(text):
    pass


def split_draw(text):
    pass


def main():
    wrapper(incurses)

    if OUTPUT:
        print(OUTPUT)


def incurses(stdscr):
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # hide cursor
    curses.curs_set(0)

    # clear screen
    stdscr.clear()

    # max window with from 0 to curses.COLS -1
    # max window height from 0 to curses.LINES -1

    # win = curses.newwin(5, 40, 7, 20)

    # text = "<a>Hover on this text<a>"
    x_text_start = 0
    # x_text_end = len(text)
    y_text = 0
    # stdscr.addstr(0, 0, text)

    # lines = {0: [(x_text_start, x_text_end, "category_1")]}
    text = """
            <a>test1</a>__<a>test2</a>
            ---<a>test2</a>

    <b>test3</b>

    <a>test3</a>"""

    new_text = parser.tree_transform(text)
    lines = parser.mapping

    stdscr.addstr(0, 0, new_text)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        stdscr.addstr(0, 0, new_text)

        if key == curses.KEY_MOUSE:
            _, x, y, _, button = curses.getmouse()
            # stdscr.addstr(10, 0, f"x, y, button = {x}, {y}, {button}")

            for lin_nr, positions in lines.items():
                line_text = new_text.splitlines(keepends=True)[lin_nr]

                for position in positions:
                    last_position = 0

                    start = position.column + 1
                    end = position.column + position.length
                    tex = line_text[start : end + 1]

                    if x >= start and x <= end and y == lin_nr:
                        stdscr.addnstr(
                            lin_nr,
                            start,
                            tex,
                            position.length,
                            curses.A_UNDERLINE,
                        )
                        stdscr.refresh()
                        if button == curses.BUTTON1_CLICKED:
                            global OUTPUT
                            OUTPUT = tex
                            return

                    stdscr.refresh()

                stdscr.refresh()


if __name__ == "__main__":
    main()
