from collections import deque
from typing import Tuple, Deque, List, Optional, Set

from grid import in_bounds, neighbors
from search import bfs_path

Pos = Tuple[int, int]

def connected(a: Pos, b: Pos, blocked: Set[Pos]) -> bool:
    return bfs_path(a, b, blocked) is not None

def simulate_one_step_and_safe(game, move: Pos) -> bool:
    """ move'u atarsam bir sonraki anda head->tail yolu var mı? """
    snake: Deque[Pos] = deque(game.snake)
    food: Optional[Pos] = game.food
    tail = snake[-1]
    will_eat = (food is not None and move == food)

    if not in_bounds(move):
        return False
    if (move in snake) and (move != tail or will_eat):
        return False

    snake.appendleft(move)
    if not will_eat:
        snake.pop()

    head = snake[0]
    tail = snake[-1]
    blocked = set(snake)
    if tail in blocked:
        blocked.remove(tail)
    return bfs_path(head, tail, blocked) is not None

def safe_neighbors(game) -> List[Pos]:
    head = game.snake[0]
    cands: List[Pos] = []
    for nb in neighbors(head):
        if simulate_one_step_and_safe(game, nb):
            cands.append(nb)
    return cands

def simulate_path_and_check_safety(game, path: List[Pos]) -> bool:
    """ Food'a giden yolu simüle et; yemden sonra head->tail mümkün mü? """
    snake: Deque[Pos] = deque(game.snake)
    food: Optional[Pos] = game.food

    if path and path[0] == snake[0]:
        path = path[1:]

    for step_cell in path:
        if not in_bounds(step_cell):
            return False
        will_eat = (food is not None and step_cell == food)
        if step_cell in snake and step_cell != snake[-1]:
            return False
        snake.appendleft(step_cell)
        if will_eat:
            food = None
        else:
            snake.pop()

    head = snake[0]
    tail = snake[-1]
    blocked = set(snake)
    blocked.remove(tail)
    return bfs_path(head, tail, blocked) is not None
