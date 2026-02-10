import os
import pygame as pg

from config import (
    CELL, COLS, ROWS, WIDTH, HEIGHT, BG_COLOR, TEXT_COL, MARGIN
)
from grid import cell_rect

# ---- ASSET YOLU ----
ASSET_DIR = os.path.join(os.path.dirname(__file__), "snake_assets")

def load_sprite(name: str) -> pg.Surface:
    """snake_assets/name.png dosyasını yükler, gerekirse CELL boyutuna ölçekler."""
    path = os.path.join(ASSET_DIR, f"{name}.png")
    try:
        img = pg.image.load(path).convert_alpha()
    except FileNotFoundError:
        print(f"HATA: {name}.png bulunamadı! snake_assets klasörünü kontrol et.")
        img = pg.Surface((CELL, CELL))
        img.fill((255, 0, 255))
        
    if img.get_width() != CELL or img.get_height() != CELL:
        img = pg.transform.smoothscale(img, (CELL, CELL))
    return img

def init_ui():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Snake AI - Görsel Modu")
    clock = pg.time.Clock()
    font = pg.font.SysFont(pg.font.get_default_font(), 22, bold=True)
    bigfont = pg.font.SysFont(pg.font.get_default_font(), 42, bold=True)

    sprites = {
        "floor": load_sprite("tile_floor"),
        "wall":  load_sprite("tile_wall"),
        "food":  load_sprite("food_apple"),
        "body":  load_sprite("snake_body_solid"),
        "head_up":    load_sprite("snake_head_solid"),
        "head_down":  load_sprite("down"),
        "head_left":  load_sprite("left"),
        "head_right": load_sprite("right"),
        "tail": load_sprite("tail")
    }

    return screen, clock, font, bigfont, sprites

# ====== ÇİZİM FONKSİYONLARI ======

def draw_tiles(screen: pg.Surface, spr_floor: pg.Surface):
    for x in range(COLS):
        for y in range(ROWS):
            screen.blit(spr_floor, cell_rect(x, y))

def draw_food(screen: pg.Surface, food, spr_food: pg.Surface):
    if food:
        screen.blit(spr_food, cell_rect(*food))

def draw_snake(screen: pg.Surface, snake, sprites: dict):
    for i, (x, y) in enumerate(snake):
        rect = cell_rect(x, y)
        if i == 0:
            if len(snake) > 1:
                neck = snake[1]
                dx, dy = x - neck[0], y - neck[1] 
                if dx == 1:    screen.blit(sprites["head_right"], rect)
                elif dx == -1: screen.blit(sprites["head_left"], rect)
                elif dy == 1:  screen.blit(sprites["head_down"], rect)
                else:          screen.blit(sprites["head_up"], rect)
            else:
                screen.blit(sprites["head_right"], rect)
        elif i == len(snake) - 1:
            before_tail = snake[i-1]
            dx, dy = before_tail[0] - x, before_tail[1] - y
            base_tail = sprites["tail"]
            if dx == 1:   rotated_tail = base_tail 
            elif dx == -1: rotated_tail = pg.transform.rotate(base_tail, 180)
            elif dy == 1:  rotated_tail = pg.transform.rotate(base_tail, -90)
            else:          rotated_tail = pg.transform.rotate(base_tail, 90)
            screen.blit(rotated_tail, rect)
        else:
            screen.blit(sprites["body"], rect)

# --- GÜNCELLENEN KISIM BURASI ---
def draw_hud(screen: pg.Surface, font: pg.font.Font, score: int, hiscore: int, status: str, seconds: float):
    # Süreyi virgülden sonra 1 basamak (ör: 12.5s) gösterecek şekilde formatladık
    info = f"Time: {seconds:.1f}s   Score: {score}   High: {hiscore}   AI: {status}   [P]ause [R]estart"
    text = font.render(info, True, TEXT_COL)
    screen.blit(text, (8, 6))

def draw_pause(screen: pg.Surface, bigfont: pg.font.Font):
    label = bigfont.render("PAUSED", True, TEXT_COL)
    rect = label.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(label, rect)

def draw_gameover(screen: pg.Surface, bigfont: pg.font.Font, font: pg.font.Font):
    over = bigfont.render("GAME OVER", True, TEXT_COL)
    tip  = font.render("Press R to restart", True, TEXT_COL)
    over_rect = over.get_rect(center=(WIDTH//2, HEIGHT//2 - 18))
    tip_rect  = tip.get_rect(center=(WIDTH//2, HEIGHT//2 + 18))
    screen.blit(over, over_rect)
    screen.blit(tip, tip_rect)