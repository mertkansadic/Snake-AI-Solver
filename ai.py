"""
Snake AI — Decision Policy (updated with Smart Finisher)

Decision pipeline:
0) FINISHER: EAT if safe (check for suicide).
1) STARVATION: Force aggressive move if stuck.
2) EARLY GAME: BFS shortest path.
3) END GAME: Circulate safely.
"""

from typing import Tuple, List, Optional
from collections import deque

from heuristics import manhattan
from grid import neighbors, in_bounds
from search import bfs_path
from simulate import safe_neighbors, simulate_path_and_check_safety, connected

Pos = Tuple[int, int]

def get_valid_moves_after_eat(game, eat_pos: Pos) -> int:
    """
    Eğer 'eat_pos' konumundaki yemi yersem, bir sonraki turda
    kafamın etrafında kaç tane geçerli (duvar/kuyruk olmayan) boşluk kalır?
    """
    # Sanal bir yılan oluştur
    sim_snake = deque(game.snake)
    sim_snake.appendleft(eat_pos)
    # Yediğimiz için kuyruğu atmıyoruz (pop yapmıyoruz), yılan uzuyor.
    
    sim_head = sim_snake[0]
    valid_count = 0
    
    # Yeni kafa pozisyonundan komşulara bak
    candidate_moves = [(sim_head[0]+1, sim_head[1]), (sim_head[0]-1, sim_head[1]),
                       (sim_head[0], sim_head[1]+1), (sim_head[0], sim_head[1]-1)]
    
    for nxt in candidate_moves:
        if in_bounds(nxt) and nxt not in sim_snake:
            valid_count += 1
            
    return valid_count

def choose_move(game) -> Pos:
    head = game.snake[0]
    body = list(game.snake)
    tail = game.snake[-1]
    
    # --- Starvation Takibi ---
    if not hasattr(game, 'moves_since_eat'):
        game.moves_since_eat = 0
        game.prev_score = game.score

    if game.score != game.prev_score:
        game.moves_since_eat = 0
        game.prev_score = game.score
    else:
        game.moves_since_eat += 1

    total_cells = game.cols * game.rows
    # Açlık Sınırı
    IS_STARVING = (game.moves_since_eat > total_cells * 2)

    # =========================================================================
    # 0) AKILLI SON VURUŞ (SMART FINISHER)
    # =========================================================================
    empty_slots = total_cells - len(game.snake)
    
    # Küçük haritalarda (6x6, 5x5) sonlara doğru devreye girer
    if empty_slots <= 3 or (total_cells < 50 and empty_slots <= 8):
        for nb in neighbors(head):
            if nb == game.food:
                # KURAL 1: Yem yılanın kendi gövdesi değil (Temel kural)
                if nb not in game.snake:
                    
                    # ÖZEL DURUM: Eğer bu SON YEM ise (Oyun Bitiyor), düşünme YE!
                    if empty_slots == 1:
                        game.status = "WINNING_MOVE"
                        return nb
                    
                    # KURAL 2 (YENİ): İntihar Kontrolü
                    # Yediğimde hareket edecek yerim kalıyor mu?
                    future_moves = get_valid_moves_after_eat(game, nb)
                    
                    if future_moves > 0:
                        game.status = "SMART_FINISH"
                        return nb
                    else:
                        # Eğer yersem öleceğim, o yüzden yeme!
                        # Normal "Circulate" moduna düşüp kuyruğu takip etsin.
                        pass

    # =========================================================================
    
    # --- stuck takibi ---
    if game.score == game.last_score and game.food == game.last_food:
        dist = manhattan(head, game.food)
        if dist >= game.last_dist:
            game.stuck_counter += 1
        else:
            game.stuck_counter = max(0, game.stuck_counter - 1)
        game.last_dist = dist
    else:
        game.stuck_counter = 0
        game.last_score = game.score
        game.last_food = game.food
        game.last_dist = manhattan(head, game.food)

    STUCK_LIMIT = game.cols + game.rows 

    # --- 1) Anti-Loop (Food locked?) ---
    blocked_except_tail = set(body)
    if tail in blocked_except_tail:
        blocked_except_tail.remove(tail)
        
    if game.food is not None and not connected(game.food, tail, blocked_except_tail):
        safe = safe_neighbors(game)
        if safe:
            fx, fy = game.food
            if game.stuck_counter > STUCK_LIMIT:
                game.jitter_phase ^= 1
                game.stuck_counter = 0

            def score_move(c: Pos):
                return (abs(c[0]-fx)+abs(c[1]-fy), manhattan(c, tail))

            safe.sort(key=score_move, reverse=True)
            choice = safe[0]
            if game.jitter_phase and len(safe) >= 2:
                choice = safe[1]
            game.status = "unlock_food_via_tail"
            return choice

    # --- KRİTİK EŞİK ---
    fill_ratio = len(game.snake) / total_cells
    force_tail_mode = (fill_ratio > 0.80)

    if IS_STARVING:
        force_tail_mode = False

    # --- 2) Yemeğe git (BFS) ---
    if not force_tail_mode:
        blocked_for_food = set(body)
        food_path = bfs_path(head, game.food, blocked_for_food)
        
        if food_path and simulate_path_and_check_safety(game, food_path):
            game.status = "shortest_to_food"
            if IS_STARVING: game.status += " (STARVING)"
            return food_path[1] if len(food_path) >= 2 else head

    # --- 3) Kuyruğa sığın ---
    safe = safe_neighbors(game)
    if safe:
        fx, fy = game.food if game.food else (head[0], head[1])

        def score_move(c: Pos):
            dist_tail = manhattan(c, tail)
            dist_food = abs(c[0]-fx)+abs(c[1]-fy)
            
            if IS_STARVING:
                return (dist_tail, -dist_food) 
            else:
                return (dist_tail, dist_food)

        safe.sort(key=score_move, reverse=True)
        
        if (IS_STARVING or game.stuck_counter > STUCK_LIMIT) and len(safe) >= 2:
             if game.moves_since_eat % 2 == 1:
                 return safe[1]

        if force_tail_mode:
            game.status = "endgame_circulate"
        else:
            game.status = "to_tail_safe"
            
        return safe[0]

    # --- 4) Fallback ---
    game.status = "fallback_safe_neighbor"
    cand: List[Pos] = []
    for nb in neighbors(head):
        cand.append(nb)
    if cand:
        fx, fy = game.food if game.food else (head[0], head[1])
        cand.sort(key=lambda c: (-abs(c[0]-fx)-abs(c[1]-fy), -manhattan(c, tail)))
        pick = cand[0]
        if game.jitter_phase and len(cand) >= 2:
            pick = cand[1]
        return pick

    return head