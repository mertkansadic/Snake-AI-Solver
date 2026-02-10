import sys
import random
from collections import deque
from typing import Tuple, Deque

import pygame as pg

from config import START_LEN, BASE_FPS, LOGIC_TPS, BG_COLOR, COLS, ROWS
from heuristics import manhattan
from physics import spawn_food, step_once
from ai import choose_move
import ui

Pos = Tuple[int, int]

class SnakeAI:
    def __init__(self):
        self.screen, self.clock, self.font, self.bigfont, self.sprites = ui.init_ui()
        random.seed(0xBEEF)
        self.cols = COLS
        self.rows = ROWS
        self.reset()

    def reset(self):
        cx, cy = self.cols // 2, self.rows // 2
        self.snake: Deque[Pos] = deque([(cx - i, cy) for i in range(START_LEN)])
        self.dir = (1, 0)
        self.alive = True
        self.paused = False
        self.score = 0
        self.hiscore = getattr(self, "hiscore", 0)
        self.food = spawn_food(self.snake)
        self.logic_accum = 0.0
        self.status = "init"
        
        # --- YENİ EKLENEN SAYAÇ ---
        self.game_time = 0.0  # Saniye cinsinden geçen süre

        # Anti-loop / stuck state
        self.last_score = 0
        self.last_food = self.food
        self.last_dist = manhattan(self.snake[0], self.food)
        self.stuck_counter = 0
        self.jitter_phase = 0

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p and self.alive:
                self.paused = not self.paused
            elif event.key == pg.K_r:
                self.reset()
            elif event.key == pg.K_ESCAPE:
                pg.quit(); sys.exit(0)

    def logic_tick(self):
        if not self.alive or self.paused:
            return
        
        # Eğer harita dolduysa (Mükemmel oyun), oyunu durdur (alive=False yapabiliriz veya özel statü verebiliriz)
        # Fizik motorunda çarpışma kontrolü var ama 'Win' durumu için buraya ekleyebilirsin.
        if len(self.snake) >= self.cols * self.rows:
             self.alive = False
             self.status = "MAP CLEARED!"
             return

        nxt = choose_move(self)
        step_once(self, nxt)

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit(0)
                self.handle_input(event)

            # Geçen gerçek zamanı (milisaniye) al
            dt_ms = self.clock.get_time()
            
            # --- SAYAÇ GÜNCELLEME ---
            # Oyun duraklatılmamışsa ve yılan yaşıyorsa süreyi arttır
            if self.alive and not self.paused:
                self.game_time += dt_ms / 1000.0

            # Mantık döngüsü (AI karar hızı)
            self.logic_accum += dt_ms / 1000.0
            step_dt = 1.0 / LOGIC_TPS
            while self.logic_accum >= step_dt:
                self.logic_tick()
                self.logic_accum -= step_dt

            # ---- ÇİZİM SIRASI ----
            self.screen.fill(BG_COLOR)
            ui.draw_tiles(self.screen, self.sprites["floor"])  
            ui.draw_food(self.screen, self.food, self.sprites["food"])  
            ui.draw_snake(self.screen, self.snake, self.sprites)  
            
            self.hiscore = max(self.hiscore, self.score)
            
            # HUD Çizimi: Artık self.game_time'ı da gönderiyoruz
            ui.draw_hud(self.screen, self.font, self.score, self.hiscore, self.status, self.game_time)
            
            if self.paused and self.alive:
                ui.draw_pause(self.screen, self.bigfont)
            if not self.alive:
                ui.draw_gameover(self.screen, self.bigfont, self.font)

            pg.display.flip()
            self.clock.tick(BASE_FPS)

if __name__ == "__main__":
    SnakeAI().run()