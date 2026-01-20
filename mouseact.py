import time
from pynput import mouse
import pyautogui as gui

def mouse_move_click(x_loc: int = None, y_loc: int = None, side: str = 'left', clicks: int = 0):
    gui.click(x_loc, y_loc, clicks, button = side, duration = 0.1)

def mouse_scroll(direct: str, step: int):
    if direct == 'up':
        gui.scroll(clicks = abs(step))
    elif direct == 'down':
        gui.scroll(clicks = -abs(step))

        