#!/usr/bin/env python3

import os
import sys
import argparse
import curses
from curses import wrapper

import canny.parser as parser
import itertools


# Mouse position: run with TERM=xterm-1003
os.environ["TERM"] = "xterm-1003"

INPUT = ""
OUTPUT = None
DEBUG = False


def main():
    global INPUT
    global DEBUG

    # command line arguments
    arg_parser = argparse.ArgumentParser(
        description="canny - a filter with a clickable interface",
    )
    arg_parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="input file",
    )
    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode",
    )

    args = arg_parser.parse_args()

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


# decorator for debugging
def debug_line_dec(stdscr):
    global DEBUG

    def wrapper(text):
        if not DEBUG:
            return
        stdscr.addstr(curses.LINES - 1, 0, text)
        stdscr.refresh()

    return wrapper


def incurses(stdscr):
    global INPUT
    global OUTPUT
    global DEBUG

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.use_default_colors()

    debug_line = debug_line_dec(stdscr)

    # hide cursor
    curses.curs_set(0)
    stdscr.scrollok(True)
    stdscr.clear()

    # parse the input
    new_text = parser.tree_transform(INPUT)
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

    last_pos = None

    while True:
        key = stdscr.getch()
        last_line = min(top_line + window_height, len(new_text_lines))

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
            debug_line(f"x,y,button={(x, y, button)}, {last_pos=}")

            # skip when mouse outside of window
            lin_nr = y + top_line
            if top_line < lin_nr > last_line:
                continue

            # scroll up
            if button == curses.BUTTON4_PRESSED:
                if top_line > 0:
                    top_line -= 1
                continue

            # scroll down
            if button == curses.BUTTON5_PRESSED:
                if top_line < len(new_text_lines) - window_height:
                    top_line += 1
                    redraw_visual_text()
                continue

            # positions for the current line
            positions = lines.get(lin_nr)

            # no positions found
            if not positions:
                continue

            # we want to start checking from the last position
            if last_pos and last_pos.line == lin_nr:
                positions.insert(0, last_pos)
            else:
                last_pos = None
                redraw_visual_text()

            line_text = new_text_lines[lin_nr]

            for index, position in enumerate(positions):
                start = position.column
                end = position.column + position.length
                pos_text = line_text[start:end]

                # check if mouse is in the position
                if x >= start and x <= end:
                    last_pos = position

                    # highlight the position
                    stdscr.addnstr(
                        y,
                        start,
                        pos_text,
                        position.length,
                        curses.A_UNDERLINE,
                    )
                    stdscr.refresh()
                    if button in (curses.BUTTON1_CLICKED, curses.BUTTON1_PRESSED):
                        global OUTPUT
                        OUTPUT = pos_text
                        return
                    break

                # last_position specific behavior
                if index == 0 and last_pos:
                    last_pos = None
                    redraw_visual_text()
                    continue


if __name__ == "__main__":
    main()
