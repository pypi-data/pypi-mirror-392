from pygame import Color, Surface, Vector2, Rect
from pygame.surfarray import make_surface

import pygame as pg
import json, os
import random
from time import time
pg.font.init()
from typing import Callable

# A workaround for the error: subprocess-exited-with-error
# Fixed by simply not packaging pygame into the package

class pygame2:
    def set_pygame(self, module):
        pass
    class Color: ...
    class Surface: ...
    class Vector2: ...
    class Rect: ...
    class font:
        def init(): ...
    class mouse:
        def get_pos(): ...
    class draw:
        def circle(): ...
        def rect(): ...

PYGAME_CALLS = pygame2()