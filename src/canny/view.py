#!/usr/bin/env python3

"""
A filter with an pointer interface 🦝
"""

# pylint: disable=global-statement, missing-function-docstring, too-many-statements, too-many-branches, too-many-locals

import os
import sys
import argparse

import logging
import traceback
import subprocess

import curses
from curses import wrapper

from canny import parser

# to capture mouse position
os.environ["TERM"] = "xterm-1003"

INPUT = ""
OUTPUT = None
DEBUG = False
USE_TAGS = False


def read_ls():
    with subprocess.Popen(["ls"], stdout=subprocess.PIPE) as proc:
        output = proc.stdout.read().decode("utf-8")
    return output


def main():
    global INPUT
    global DEBUG
    global USE_TAGS

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
    arg_parser.add_argument(
        "--tags",
        action="store_true",
        help="parse html tags",
    )

    args = arg_parser.parse_args()

    # check if it is a pipe
    is_pipe = not os.isatty(sys.stdin.fileno())

    try:
        if args.tags:
            USE_TAGS = True

        if args.debug:
            DEBUG = True
            logging.basicConfig(
                filename="some.log", encoding="utf-8", level=logging.DEBUG
            )

        if is_pipe or args.input == "-":
            INPUT = sys.stdin.read()

            # redirect stdin to /dev/tty
            with open("/dev/tty", encoding="utf-8") as f:
                os.dup2(f.fileno(), 0)

        elif not args.input and not is_pipe:
            INPUT = read_ls()

        elif args.input:
            if not os.path.isfile(args.input):
                print(f"File '{args.input}' does not exist")
                sys.exit(1)

            with open(args.input, "r", encoding="utf-8") as f:
                INPUT = f.read()
        else:
            pass

        stdout = os.dup(sys.stdout.fileno())
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

        try:
            wrapper(incurses)
        except curses.error as e:
            if str(e) == "setupterm: could not find terminal":
                print("Error: ", e, end="\n\n")
                print("Check if xterm-1003 is installed (present in terminfo dirs)")
                print("\tapt install ncurses-term  (ubuntu)\n")
            else:
                print(repr(e))
            sys.exit(1)
        except Exception as e:
            if DEBUG:
                traceback.print_exc()

            print("Error: ", e)
            sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(1)

    if OUTPUT:
        os.dup2(stdout, sys.stdout.fileno())
        print(OUTPUT)


# decorator for debugging
def debug_line_dec(log):
    # global DEBUG

    def debug_wrapper(args):
        if not DEBUG:
            return
        log.debug(args)

    return debug_wrapper


def incurses(stdscr):
    global OUTPUT

    stdscr.keypad(True)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.use_default_colors()

    log = debug_line_dec(logging)

    # hide cursor
    curses.curs_set(0)
    stdscr.scrollok(True)
    stdscr.clear()

    # parse the input
    new_text = parser.tree_transform(INPUT, html=USE_TAGS)
    new_text_lines = new_text.splitlines(keepends=True)
    lines = parser.MAPPING

    wh, _ = stdscr.getmaxyx()
    window_height = wh - 2 if DEBUG else wh - 1

    top_line = 0
    last_line = top_line + window_height - 1

    # kinda hacky
    def redraw_visual_text():
        stdscr.addstr(0, 0, "".join(new_text_lines[top_line : (last_line + 1)]))
        stdscr.refresh()

    redraw_visual_text()

    last_pos = None

    # update the last line based on the top line
    def update_lastline(top):
        return min(top + window_height - 1, len(new_text_lines) - 1)

    while True:
        curses.flushinp()
        key = stdscr.getch()
        last_line = update_lastline(top_line)

        if key == curses.KEY_DOWN:
            if top_line < len(new_text_lines) - window_height:
                top_line += 1
                last_line = update_lastline(top_line)
                redraw_visual_text()
            continue
        if key == curses.KEY_UP:
            if top_line > 0:
                top_line -= 1
                last_line = update_lastline(top_line)
                redraw_visual_text()
            continue
        if key == ord("q"):
            break
        if key == curses.KEY_MOUSE:
            _, x, y, _, button = curses.getmouse()
            log(f"x,y,button={(x, y, button)}, {last_pos=}, {curses.keyname(button)}")

            # skip when mouse outside of window
            lin_nr = y + top_line
            if top_line < lin_nr > last_line:
                continue

            # scroll up
            if button == curses.BUTTON4_PRESSED:
                if top_line > 0:
                    top_line -= 1
                    last_line = update_lastline(top_line)
                    redraw_visual_text()
                continue

            # scroll down
            if button == curses.BUTTON5_PRESSED:
                if top_line < len(new_text_lines) - window_height:
                    top_line += 1
                    last_line = update_lastline(top_line)
                    redraw_visual_text()
                continue

            # positions for the current line
            optional = lines.get(lin_nr)
            if not optional:
                last_pos = None
                redraw_visual_text()
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
                if start <= x <= end:
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
