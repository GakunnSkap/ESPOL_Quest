# engine/ui.py
import pygame
from core.config import COLOR_HUD, VIRTUAL_W

class HUD:
    def __init__(self, player, level):
        self.player = player
        self.level = level
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 22)
        self.margin = 16
        self.heart_size = 18
        self.energy_w = 160
        self.energy_h = 12

    def draw(self, screen):
        x, y = self.margin, self.margin

        # 1) Vida
        for i in range(self.player.max_hp):
            color = (255, 80, 80) if i < self.player.hp else (60, 30, 30)
            pygame.draw.rect(screen, color, (x + i * (self.heart_size + 4), y, self.heart_size, self.heart_size))

        # 2) Energía
        pool = self.player.energy_pool
        pct = pool.energy / pool.max_energy
        bar_x = self.margin
        bar_y = y + self.heart_size + 10
        pygame.draw.rect(screen, (40, 60, 80), (bar_x, bar_y, self.energy_w, self.energy_h))
        pygame.draw.rect(screen, (80, 200, 255), (bar_x, bar_y, int(self.energy_w * pct), self.energy_h), border_radius=3)

        # 3) Enemigos vivos
        text = f"Enemigos: {len(self.level.enemies)}"
        surf = self.font.render(text, True, (200, 220, 255))
        screen.blit(surf, (VIRTUAL_W - surf.get_width() - 20, self.margin))

        # 4) Nombre del nivel
        if hasattr(self.level, "level_name"):
            surf2 = self.big_font.render(self.level.level_name, True, (200, 220, 255))
            screen.blit(surf2, (VIRTUAL_W/2 - surf2.get_width()/2, 10))

    def draw_boss_bar(self, screen, entity, title="BOSS"):
        if not entity or not getattr(entity, "alive", False):
            return
        total_w = int(0.62 * VIRTUAL_W)
        total_h = 16
        x = (VIRTUAL_W - total_w) // 2
        y = 60
        pygame.draw.rect(screen, (35, 20, 20), (x, y, total_w, total_h))
        pygame.draw.rect(screen, (120, 40, 40), (x, y, total_w, total_h), 2)
        pct = max(0, entity.hp) / max(1, getattr(entity, "max_hp", 1))
        fill_w = int(total_w * pct)
        pygame.draw.rect(screen, (255, 80, 80), (x, y, fill_w, total_h))
        label = f"{title}  {entity.hp}/{entity.max_hp}"
        surf = self.font.render(label, True, (230, 220, 220))
        screen.blit(surf, (VIRTUAL_W/2 - surf.get_width()/2, y - 22))
