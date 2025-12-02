# entities/enemy.py
import pygame
from engine.entity import Entity
from engine.physics import move_and_collide, apply_gravity
from engine.combat import Team, DamageEvent

class EnemyBase(Entity):
    def __init__(self, x, y, w=26, h=30, color=(255, 120, 120)):
        super().__init__(x, y, w, h, color)
        self.team = Team.ENEMY
        self.use_gravity = True
        self.on_ground = False
        self.max_hp = 3
        self.hp = self.max_hp
        self.damage = 1
        self.speed = 60
        self.facing = -1
        self.patrol_range = (x - 60, x + 60)
        self.start_x = x
        self.tags = {"enemy"}
        self.dead = False
        self.is_boss = False
        self.is_miniboss = False

        # Mostrar barra de vida temporalmente al recibir daño
        self.show_hp_timer = 0.0
        self.show_hp_duration = 2.5
        self.hpbar_fade = True

    def patrol_ai(self, dt, tiles):
        if self.dead:
            return
        self.vel.x = self.facing * self.speed
        move_and_collide(self, tiles, dt)
        if self.rect.left <= self.patrol_range[0]:
            self.facing = 1
        elif self.rect.right >= self.patrol_range[1]:
            self.facing = -1

    def take_damage(self, dmg_event: DamageEvent):
        if self.dead:
            return
        dmg = getattr(dmg_event, "amount", 1)
        self.hp -= dmg
        self.show_hp_timer = self.show_hp_duration
        if self.hp <= 0:
            self.dead = True
            self.alive = False

    def update(self, dt, world):
        if not self.alive:
            return
        tiles = getattr(world, "tiles", [])
        apply_gravity(self, dt)
        self.patrol_ai(dt, tiles)
        if self.show_hp_timer > 0:
            self.show_hp_timer -= dt
            if self.show_hp_timer < 0:
                self.show_hp_timer = 0

    def _health_fill_color(self, pct: float):
        if pct > 0.6:
            return (120, 255, 120)
        elif pct > 0.3:
            return (255, 220, 120)
        else:
            return (255, 120, 120)

    def _draw_health_bar(self, screen):
        bar_w = self.rect.w
        bar_h = 4
        x = self.rect.x
        y = self.rect.y - (bar_h + 4)

        pct = max(0.0, self.hp) / max(1, self.max_hp)

        # Alpha (fade): 255 → 0
        a = int(255 * min(1.0, self.show_hp_timer / self.show_hp_duration)) if self.hpbar_fade else 255

        bar = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bar.fill((40, 40, 40, int(a * 0.75)))

        fill_w = max(0, int(bar_w * pct))
        fill_color = self._health_fill_color(pct) + (a,)
        if fill_w > 0:
            pygame.draw.rect(bar, fill_color, (0, 0, fill_w, bar_h))

        # Blit + borde
        screen.blit(bar, (x, y))
        pygame.draw.rect(screen, (12, 12, 12), (x, y, bar_w, bar_h), 1)

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, self.color, self.rect)
        if (not self.is_boss and not self.is_miniboss and self.hp < self.max_hp and self.show_hp_timer > 0):
            self._draw_health_bar(screen)
