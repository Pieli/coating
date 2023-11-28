#!/usr/bin/env python3

import os
import sys
import argparse
import curses
from curses import wrapper

import logging
import itertools

import canny.parser as parser


# ubuntu
# - check if ncurses-term (apt) is needed
# - initial ungetmouse() call
# - check if additional parameters are needed
# - check out scroll


# Mouse position: run with TERM=xterm-1003
os.environ["TERM"] = "xterm-1003"

INPUT = ""
OUTPUT = None
DEBUG = False

logging.basicConfig(filename="some.log", encoding="utf-8", level=logging.DEBUG)


def read_ls():
    import subprocess

    proc = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
    proc.wait()
    return proc.stdout.read().decode("utf-8")


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

        if not args.input:
            INPUT = read_ls()

        elif not args.input or args.input.strip() == "-":
            INPUT = sys.stdin.read()

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

    stdscr.keypad(True)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)

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
    window_height = wh - 2 if DEBUG else wh - 1

    top_line = 0
    last_line = top_line + window_height - 1

    # kinda hacky
    def redraw_visual_text():
        stdscr.addstr(0, 0, "".join(new_text_lines[top_line : (last_line + 1)]))
        stdscr.refresh()

    redraw_visual_text()

    logging.debug(f"{window_height=}")

    # for ubuntu (not changing the bstate on movement)
    curses.ungetmouse(curses.KEY_MOUSE, 0, 0, 0, curses.BUTTON_ALT)

    last_pos = None

    # update the last line based on the top line
    update_lastline = lambda top: min(top + window_height - 1, len(new_text_lines) - 1)

    while True:
        curses.flushinp()
        key = stdscr.getch()
        last_line = update_lastline(top_line)

        # logging.debug(f"{curses.keyname(key)}")

        if key == curses.KEY_DOWN:
            if top_line < len(new_text_lines) - window_height:
                top_line += 1
                last_line = update_lastline(top_line)
                redraw_visual_text()
            continue
        elif key == curses.KEY_UP:
            if top_line > 0:
                top_line -= 1
                last_line = update_lastline(top_line)
                redraw_visual_text()
            continue
        elif key == ord("q"):
            break
        elif key == curses.KEY_MOUSE:
            _, x, y, z, button = curses.getmouse()
            logging.debug(
                f"x,y,button={(x, y, button)}, {last_pos=}, {curses.keyname(button)}"
            )

            # skip when mouse outside of window
            lin_nr = y + top_line
            if top_line < lin_nr > last_line:
                continue

            logging.debug(f"lin_nr={lin_nr}, top_line={top_line}, y={y}, {last_line=}")

            # scroll up
            if button == curses.BUTTON4_PRESSED:
                if top_line > 0:
                    top_line -= 1
                    last_line = update_lastline(top_line)
                    redraw_visual_text()
                    # for ubuntu (not changing the bstate on movement)
                    # curses.ungetmouse(curses.KEY_MOUSE, 0, 0, 0, curses.BUTTON_ALT)
                continue

            # scroll down
            if button == curses.BUTTON5_PRESSED:
                if top_line < len(new_text_lines) - window_height:
                    top_line += 1
                    last_line = update_lastline(top_line)
                    redraw_visual_text()
                    # for ubuntu (not changing the bstate on movement)
                    # curses.ungetmouse(curses.KEY_MOUSE, 0, 0, 0, curses.BUTTON_ALT)
                continue

            # positions for the current line
            optional = lines.get(lin_nr)
            if not optional:
                continue

            # copy to prevent changing the original
            positions = optional.copy()

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
        else:
            pass


if __name__ == "__main__":
    main()