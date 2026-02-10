"""
Snake AI — Algorithms Summary (updated 2025-11-05 12:18)

This module implements **Breadth-First Search (BFS)** on a 4-neighborhood grid.
- Purpose: find a shortest path from `start` to `goal` avoiding `blocked` cells.
- Complexity (per call): **O(V+E) = O(m·n)** on an m×n grid (E≈4V).
- Size agnostic: uses `grid.neighbors()` which consults `config.COLS/ROWS`.

"""

from collections import deque
from typing import Optional, Set, Tuple, List

from grid import neighbors

Pos = Tuple[int, int]

def bfs_path(start: Pos, goal: Optional[Pos], blocked: Set[Pos]) -> Optional[List[Pos]]:
    """start->goal en kısa yol (blocked: set[(x,y)])"""
    if goal is None or start == goal:
        return [start]
    q = deque([start])
    came = {start: None}
    while q:
        u = q.popleft()
        for v in neighbors(u):
            if v in blocked or v in came:
                continue
            came[v] = u
            if v == goal:
                path = [v]
                while path[-1] is not None:
                    path.append(came[path[-1]])
                path.pop()
                path.reverse()
                return path
            q.append(v)
    return None
