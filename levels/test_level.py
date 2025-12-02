# levels/test_level.py
from levels.level_base import LevelBase
from core.config import VIRTUAL_W, VIRTUAL_H

class TestLevel(LevelBase):
    def __init__(self, game):
        super().__init__(game)
        self.level_name = "Nivel de Prueba (escala 128x128)"

        # Parámetros base (más grandes)
        ground_y = VIRTUAL_H - 160     # suelo más abajo
        wall_w   = 48                  # muros más gruesos
        step_h   = 120                 # altura entre plataformas
        step_w   = 240                 # ancho de plataformas

        # --- Suelo y paredes laterales ---
        self.add_tile(-wall_w, 0, wall_w, VIRTUAL_H)             # izquierda
        self.add_tile(VIRTUAL_W, 0, wall_w, VIRTUAL_H)           # derecha
        self.add_tile(0, ground_y, VIRTUAL_W, 80)                # suelo

        # --- Torres verticales ---
        # Izquierda
        base_x = 160
        for i in range(5):
            self.add_tile(base_x, ground_y - 60 - i * step_h, step_w, 32)

        # Centro
        base_x = 520
        for i in range(5):
            self.add_tile(base_x, ground_y - 90 - i * step_h, step_w, 32)

        # Derecha
        base_x = 880
        for i in range(5):
            self.add_tile(base_x, ground_y - 60 - i * step_h, step_w, 32)

        # --- Islas altas ---
        self.add_tile(360, ground_y - 640, 280, 32)
        self.add_tile(760, ground_y - 700, 320, 32)

        # --- Reposicionar jugador ---
        self.player.rect.topleft = (120, ground_y - 200)

        # --- Enemigos (distintos niveles) ---
        self.spawn_enemy(200, ground_y - 120)
        self.spawn_enemy(540, ground_y - 220)
        self.spawn_enemy(900, ground_y - 180)
        self.spawn_enemy(400, ground_y - 660)
        self.spawn_enemy(820, ground_y - 720)





