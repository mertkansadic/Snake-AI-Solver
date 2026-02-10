from typing import Tuple, Optional

Pos = Tuple[int, int]

def manhattan(a: Optional[Pos], b: Optional[Pos]) -> int:
    if a is None or b is None:
        return 0
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
