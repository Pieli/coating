import os
import curses
from curses import wrapper


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


def draw_to_screen(text):
    pass


def split_draw(text):
    pass


def main(stdscr):
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # clear screen
    stdscr.clear()

    # max window with from 0 to curses.COLS -1
    # max window height from 0 to curses.LINES -1

    # win = curses.newwin(5, 40, 7, 20)

    text = "<a>Hover on this text<a>"
    x_text_start = 0
    x_text_end = len(text)
    y_text = 0
    stdscr.addstr(0, 0, text)
    stdscr.refresh()

    lines = {0: [(x_text_start, x_text_end, "category_1")]}

    while True:
        key = stdscr.getch()
        stdscr.addstr(0, 0, text)

        if key == curses.KEY_MOUSE:
            _, x, y, _, button = curses.getmouse()
            stdscr.addstr(1, 0, f"x, y, button = {x}, {y}, {button}")

            for part in lines.get(y, ()):
                start, end, category = part
                if x >= start and x <= end:
                    stdscr.addstr(y, start, text, curses.A_UNDERLINE)
                    stdscr.refresh()
            stdscr.refresh()


wrapper(main)
