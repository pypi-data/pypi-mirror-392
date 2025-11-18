import sys
import shutil
import time
import pygame_sdl2
import queue

from cetragm import config

MENU_COLOR_SELECTED = "\x1b;38;2;127;255;212m"
MENU_COLOR_NORMAL   = "\x1b;38;2;220;220;220m"
MENU_COLOR_VALUE    = "\x1b;38;2;13;152;186m"

def center_lines(lines):
    term = shutil.get_terminal_size()
    max_width = max(len(ln) for ln in lines) if lines else 0
    