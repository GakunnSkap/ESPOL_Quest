# entities/bullet.py
import pygame
from engine.entity import Entity
from engine.combat import DamageEvent, Team

class Bullet(Entity):
    def __init__(self, x, y, direction=1, speed=500, damage=1,
                 lifespan=1.5, color=(255, 255, 255), tags=None):
        # Guardamos color aquí mismo
        super().__init__(x, y, 8, 4, color)
        self.team = Team.PLAYER
        self.vel.x = direction * speed
        self.damage = damage
        self.timer = 0.0
        self.lifespan = lifespan
        self.color = color       
        self.tags = set(tags or [])

    def update(self, dt, world):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.alive = False
            return

        self.rect.x += int(self.vel.x * dt)

        # Colisión con enemigos
        for en in getattr(world, "enemies", []):
            if not en.alive:
                continue
            if self.rect.colliderect(en.rect):
                event = DamageEvent(amount=self.damage, tags=self.tags, source=self)
                en.take_damage(event)
                self.alive = False
                break

    def draw(self, screen):
        # Usa self.color para cada bala
        pygame.draw.rect(screen, self.color, self.rect)
