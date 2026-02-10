"""
Snake AI — Grid Primitives (updated 2025-11-05 12:18)

This module centralizes the grid geometry:
- `in_bounds((x,y))` enforces 0≤x<COLS and 0≤y<ROWS using `config`.
- `neighbors((x,y))` returns 4-neighborhood valid cells.
All other modules rely on these to stay correct for any m×n dimensions.

"""

from typing import Tuple, List
from pygame import Rect
import pygame as pg

from config import CELL, COLS, ROWS

Pos = Tuple[int, int]

def cell_rect(x: int, y: int) -> Rect:
    return pg.Rect(x * CELL, y * CELL, CELL, CELL)

def in_bounds(pos: Pos) -> bool:
    x, y = pos
    return 0 <= x < COLS and 0 <= y < ROWS

def neighbors(pos: Pos) -> List[Pos]:
    x, y = pos
    cand = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    return [p for p in cand if in_bounds(p)]
