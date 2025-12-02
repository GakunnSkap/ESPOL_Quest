# engine/physics.py
import pygame
from core.config import GRAVITY, MAX_FALL_SPEED

def apply_gravity(entity, dt: float):
    """Aplica gravedad si la entidad la usa, con clamp a velocidad terminal."""
    if hasattr(entity, "use_gravity") and not entity.use_gravity:
        return
    # clamp después de sumar para evitar overshoot
    entity.vel.y = min(entity.vel.y + GRAVITY * dt, MAX_FALL_SPEED)

def move_and_collide(entity, tiles, dt: float):
    """Desplaza entidad y maneja colisiones con lista de tiles (AABB)."""

    # --- Eje X ---
    entity.rect.x += int(entity.vel.x * dt)
    for t in tiles:
        if entity.rect.colliderect(t):
            if entity.vel.x > 0:
                entity.rect.right = t.left
            elif entity.vel.x < 0:
                entity.rect.left = t.right

    # --- Eje Y ---
    entity.rect.y += int(entity.vel.y * dt)
    if hasattr(entity, "on_ground"):
        entity.on_ground = False

    for t in tiles:
        if entity.rect.colliderect(t):
            if entity.vel.y > 0:
                entity.rect.bottom = t.top
                entity.vel.y = 0
                if hasattr(entity, "on_ground"):
                    entity.on_ground = True
            elif entity.vel.y < 0:
                entity.rect.top = t.bottom
                entity.vel.y = 0
