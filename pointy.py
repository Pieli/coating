import os
import argparse
import curses
from curses import wrapper

import parser


# Mouse position: run with TERM=xterm-1003
os.environ["TERM"] = "xterm-1003"


# TODO
# * make setup.py
# * make readme.md
# * draw in different colors
# * whitespace if no tag is specified
# * fix pipe to output
# * ncurses scroll? -> start with fixed


INPUT = ""
OUTPUT = None
DEBUG = False


def main():
    global INPUT
    global DEBUG

    # command line arguments
    parser = argparse.ArgumentParser(
        description="Pointy - a ncurses based text editor",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="input file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode",
    )

    args = parser.parse_args()

    if args.debug:
        DEBUG = True

    if args.input:
        if args.input.strip() == "-":
            import sys

            text = sys.stdin.read()
            INPUT = text

        else:
            if not os.path.isfile(args.input):
                print(f"File '{args.input}' does not exist")
                exit(1)

            with open(args.input, "r") as f:
                INPUT = f.read()

    wrapper(incurses)

    if OUTPUT:
        print(OUTPUT)


def incurses(stdscr):
    global INPUT
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.use_default_colors()

    # hide cursor
    curses.curs_set(0)

    # clear screen
    stdscr.clear()

    # max window with from 0 to curses.COLS -1
    # max window height from 0 to curses.LINES -1
    # win = curses.newwin(5, 40, 7, 20)

    # TODO remove later
    if not INPUT:
        text = """

            Are you okay?

        <a>[Yes]</a>           <a>[No]</a>
        """
    else:
        text = INPUT

    new_text = parser.tree_transform(text)
    lines = parser.MAPPING

    stdscr.addstr(0, 0, new_text)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        stdscr.addstr(0, 0, new_text)

        if key == curses.KEY_MOUSE:
            _, x, y, _, button = curses.getmouse()
            if DEBUG:
                stdscr.addstr(curses.LINES - 1, 0, f"x, y, button = {x}, {y}, {button}")

            for lin_nr, positions in lines.items():
                line_text = new_text.splitlines(keepends=True)[lin_nr]

                for position in positions:
                    start = position.column + 1
                    end = position.column + position.length
                    tex = line_text[start : end + 1]

                    if y == lin_nr and x >= start and x <= end:
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
