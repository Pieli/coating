import curses
from curses import wrapper


# Mouse position: run with TERM=xterm-1003


def main(stdscr):
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # clear screen
    stdscr.clear()

    # max window with from 0 to curses.COLS -1
    # max window height from 0 to curses.LINES -1

    # win = curses.newwin(5, 40, 7, 20)

    text = "Hover on this text"
    x_text_start = 0
    x_text_end = len(text)
    y_text = 0
    stdscr.addstr(0, 0, text)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        stdscr.addstr(0, 0, text)
        if key == curses.KEY_MOUSE:
            _, x, y, _, button = curses.getmouse()
            stdscr.addstr(1, 0, "x, y, button = {}, {}, {}".format(x, y, button))
            if y == y_text and x >= x_text_start and x <= x_text_end:
                stdscr.addstr(0, 0, text, curses.A_UNDERLINE)
                stdscr.refresh()
        stdscr.refresh()


wrapper(main)
