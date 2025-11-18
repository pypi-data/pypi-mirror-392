import pyautogui
from pyautogui import moveTo, position, size
from time import sleep, time
from random import randint

from ratisbona_utils.io import errprint

from ratisbona_utils.boxdrawing import blue_dosbox

r_jiggle = 10
d_border = 10


def min_bounce(coord, themin, distance):
    if coord < themin + distance:
        return themin + 2 * distance
    return coord


def max_bounce(coord, themax, distance):
    if coord > themax - distance:
        return themax - 2 * distance
    return coord


def wiggle_wiggle():

    while True:
        cx, cy = position()
        sx, sy = size()
        x, y = cx + randint(-r_jiggle, +r_jiggle), cy + randint(-r_jiggle, +r_jiggle)
        x, y = min_bounce(x, 0, d_border), min_bounce(y, 0, d_border)
        x, y = max_bounce(x, sx, d_border), max_bounce(y, sy, d_border)
        moveTo(x, y)
        sleep(1)

