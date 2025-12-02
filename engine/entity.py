# engine/entity.py
import pygame

class Entity:
    """
    Clase base para todos los objetos del mundo (jugador, enemigo, bala, item...).
    Define posición, colisiones y ciclo básico update/draw.
    """
    def __init__(self, x, y, w, h, color=(255,255,255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.vel = pygame.Vector2(0, 0)
        self.color = color
        self.alive = True
        self.facing = 1
        self.layer = 0   # usado más adelante para dibujar por orden (UI, fondo, etc.)
        self.team = "NEUTRAL"  # puede ser PLAYER, ENEMY, ALLY, NEUTRAL
        self.tags = set()      # elemental tags (electric, time, bio, etc.)

    def update(self, dt, world):
        """Actualiza estado (posición, IA, timers, etc.)"""
        pass

    def draw(self, screen):
        """Dibujo placeholder."""
        pygame.draw.rect(screen, self.color, self.rect)

    def kill(self):
        self.alive = False
