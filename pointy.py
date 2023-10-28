#!/usr/bin/env python3

import os
import sys
import argparse
import curses
from curses import wrapper

import parser


# Mouse position: run with TERM=xterm-1003
os.environ["TERM"] = "xterm-1003"


# TODO
# * make setup.py
# * make readme.md


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

    try:
        if args.debug:
            DEBUG = True

        if not args.input or args.input.strip() == "-":
            text = sys.stdin.read()
            INPUT = text

            with open("/dev/tty") as f:
                os.dup2(f.fileno(), 0)

        elif args.input:
            if not os.path.isfile(args.input):
                print(f"File '{args.input}' does not exist")
                exit(1)

            with open(args.input, "r") as f:
                INPUT = f.read()
        else:
            pass

        stdout = os.dup(sys.stdout.fileno())
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

        wrapper(incurses)
    except KeyboardInterrupt:
        exit(1)

    if OUTPUT:
        os.dup2(stdout, sys.stdout.fileno())
        print(OUTPUT)


def incurses(stdscr):
    global INPUT
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.use_default_colors()

    # hide cursor
    curses.curs_set(0)
    stdscr.scrollok(True)
    stdscr.clear()

    text = INPUT

    new_text = parser.tree_transform(text)
    new_text_lines = new_text.splitlines(keepends=True)
    lines = parser.MAPPING

    wh, window_width = stdscr.getmaxyx()
    window_height = wh - 1 if DEBUG else wh

    top_line = 0
    last_line = top_line + window_height

    # kinda hacky
    def redraw_visual_text():
        stdscr.addstr(0, 0, "".join(new_text_lines[top_line:last_line]))
        stdscr.refresh()

    redraw_visual_text()

    while True:
        key = stdscr.getch()
        last_line = min(top_line + window_height, len(new_text_lines))
        redraw_visual_text()

        if key == curses.KEY_DOWN:
            if top_line < len(new_text_lines) - window_height:
                top_line += 1
                redraw_visual_text()
            continue
        elif key == curses.KEY_UP:
            if top_line > 0:
                top_line -= 1
            continue
        elif key == ord("q"):
            break

        if key == curses.KEY_MOUSE:
            _, x, y, z, button = curses.getmouse()
            if DEBUG:
                stdscr.addstr(
                    curses.LINES - 1,
                    0,
                    f"x, y, button = {x}, {y}, {z}, {button}, y_adj {y + top_line}",
                )

            lin_nr = y + top_line
            if top_line < lin_nr > last_line:
                continue

            # scroll
            if button == curses.BUTTON4_PRESSED:
                if top_line > 0:
                    top_line -= 1
                continue

            if button == curses.BUTTON5_PRESSED:
                if top_line < len(new_text_lines) - window_height:
                    top_line += 1
                    redraw_visual_text()
                continue

            positions = lines.get(lin_nr)
            if not positions:
                continue

            line_text = new_text_lines[lin_nr]

            for position in positions:
                start = position.column
                end = position.column + position.length
                tex = line_text[start:end]

                if x >= start and x <= end:
                    stdscr.addnstr(
                        y,
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


if __name__ == "__main__":
    main()
