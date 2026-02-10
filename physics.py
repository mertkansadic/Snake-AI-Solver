"""
Snake AI — Physics & Rules (updated 2025-11-05 12:18)

Implements collision rules with tail exception and growth, plus uniform random
food spawning from the set of empty cells. All logic is parameterized by
`config.COLS/ROWS` and thus correct for any board size.

"""

import random
from collections import deque
from typing import Tuple, Deque, Optional, Set

from config import COLS, ROWS
from grid import in_bounds
Pos = Tuple[int, int]

def spawn_food(snake: Deque[Pos]) -> Optional[Pos]:
    empty: Set[Pos] = {(x, y) for x in range(COLS) for y in range(ROWS)} - set(snake)
    return random.choice(tuple(empty)) if empty else None

def step_once(game, nxt: Pos) -> None:
    """Gerçek oyunda bir hamle uygula (doğru kuyruk kuralıyla)."""
    if not in_bounds(nxt):
        game.alive = False
        return

    tail = game.snake[-1]
    will_eat = (game.food is not None and nxt == game.food)

    # Çarpışma (tail istisnası)
    if (nxt in game.snake) and (nxt != tail or will_eat):
        game.alive = False
        return

    game.snake.appendleft(nxt)
    if will_eat:
        game.score += 1
        game.food = spawn_food(game.snake)
    else:
        game.snake.pop()
