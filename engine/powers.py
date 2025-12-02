# engine/powers.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Set, List
from entities.bullet import Bullet
from engine.combat import DamageEvent
import pygame
# ─────────────────────────────────────────────────────────
# Energía para poderes
# ─────────────────────────────────────────────────────────
@dataclass
class EnergyPool:
    max_energy: float = 100.0
    energy: float = 100.0
    regen_rate: float = 10.0  # por segundo

    def can_spend(self, amount: float) -> bool:
        return self.energy >= amount

    def spend(self, amount: float) -> bool:
        if self.can_spend(amount):
            self.energy -= amount
            if self.energy < 0:
                self.energy = 0
            return True
        return False

    def regen(self, dt: float):
        if self.energy < self.max_energy:
            self.energy += self.regen_rate * dt
            if self.energy > self.max_energy:
                self.energy = self.max_energy


# ─────────────────────────────────────────────────────────
# Enfriamientos por poder (cooldowns)
# ─────────────────────────────────────────────────────────
@dataclass
class CooldownTracker:
    cooldown_ms=50
    last_use_ms: int = -10_000_000  # suficientemente en el pasado

    def ready(self, now_ms: int) -> bool:
        return (now_ms - self.last_use_ms) >= self.cooldown_ms

    def mark_used(self, now_ms: int):
        self.last_use_ms = now_ms


# ─────────────────────────────────────────────────────────
# Interfaz base de un poder
# ─────────────────────────────────────────────────────────
@dataclass
class Power:
    name: str
    energy_cost: float = 0.0
    cooldown_ms: int = 0
    out_tags: Set[str] = field(default_factory=set)

    # El motor asignará estos al equipar el poder:
    cd: CooldownTracker = field(default_factory=CooldownTracker, init=False)

    # Reglas de uso
    def can_use(self, player, world, now_ms: int) -> bool:
        # Chequeo genérico: cooldown + energía
        if not self.cd.ready(now_ms):
            return False
        pool: Optional[EnergyPool] = getattr(player, "energy_pool", None)
        if pool is None:
            return True  # si no hay energía aún, dejar usar (beta)
        return pool.can_spend(self.energy_cost)

    # Efecto (a implementar en poderes concretos)
    def use(self, player, world, now_ms: int) -> bool:
        """
        Debe ser implementado por subclases: crear bullet/fieldzone/summon/etc.
        Debe llamar a self.commit_use(player, now_ms) si se ejecuta.
        Retorna True si se ejecutó, False si no.
        """
        raise NotImplementedError

    # Commit (gasta energía + prende cooldown)
    def commit_use(self, player, now_ms: int):
        pool: Optional[EnergyPool] = getattr(player, "energy_pool", None)
        if pool:
            pool.spend(self.energy_cost)
        self.cd.cooldown_ms = self.cooldown_ms
        self.cd.mark_used(now_ms)


# ─────────────────────────────────────────────────────────
# Conjunto de poderes equipados (ataque base + 2 habilidades)
# ─────────────────────────────────────────────────────────
@dataclass
class PowerSet:
    primary: Optional[Power] = None  # J (o básico)
    skill1: Optional[Power] = None   # K
    skill2: Optional[Power] = None   # L

    # Opcional: rotación de loadouts (Q/R)
    loadouts: List["PowerSet"] = field(default_factory=list)
    idx: int = 0

    def active(self) -> "PowerSet":
        # Si existe una lista de loadouts, devuelve el actual; si no, a sí mismo.
        if self.loadouts:
            return self.loadouts[self.idx]
        return self

    def next_loadout(self):
        if self.loadouts:
            self.idx = (self.idx + 1) % len(self.loadouts)

    def prev_loadout(self):
        if self.loadouts:
            self.idx = (self.idx - 1) % len(self.loadouts)

    # Helpers de uso (el player llamará a estos)
    def try_primary(self, player, world, now_ms: int) -> bool:
        p = self.active().primary
        return p.can_use(player, world, now_ms) and p.use(player, world, now_ms) if p else False

    def try_skill1(self, player, world, now_ms: int) -> bool:
        p = self.active().skill1
        return p.can_use(player, world, now_ms) and p.use(player, world, now_ms) if p else False

    def try_skill2(self, player, world, now_ms: int) -> bool:
        p = self.active().skill2
        return p.can_use(player, world, now_ms) and p.use(player, world, now_ms) if p else False

class SimpleShotPower(Power):
    def __init__(self, name, color, energy_cost=10, cooldown_ms=800,
                 speed=520, damage=1, lifespan=1.2, out_tags=None):
        super().__init__(name=name, energy_cost=energy_cost,
                         cooldown_ms=cooldown_ms, out_tags=set(out_tags or []))
        self.color = color
        self.speed = speed
        self.damage = damage
        self.lifespan = lifespan

    def use(self, player, world, now_ms):
        dir_ = 1 if player.facing >= 0 else -1
        x = player.rect.centerx + dir_ * 14
        y = player.rect.centery
        world.bullets.append(
            Bullet(x, y, direction=dir_, speed=self.speed, damage=self.damage,
                   lifespan=self.lifespan, color=self.color, tags=self.out_tags)
        )
        self.commit_use(player, now_ms)
        return True
class MeleePower(Power):
    """
    Golpe corto alcance activado por voz.
    Respeta energía/cooldown y puede activar reactivos por tags.
    """
    def __init__(self, name,
                 energy_cost=0, cooldown_ms=280,
                 range_px=22, w=18, h=16,
                 damage=1, knockback=(120, -60),
                 out_tags=None):
        super().__init__(name=name, energy_cost=energy_cost,
                         cooldown_ms=cooldown_ms,
                         out_tags=set(out_tags or {"melee"}))
        self.range_px = range_px
        self.w = w
        self.h = h
        self.damage = damage
        self.knockback = knockback

    def _hitbox(self, player):
        if player.facing >= 0:
            hx = player.rect.right + self.range_px
        else:
            hx = player.rect.left - self.range_px - self.w
        hy = player.rect.centery - self.h // 2
        return pygame.Rect(hx, hy, self.w, self.h)

    def use(self, player, world, now_ms):
        hb = self._hitbox(player)

        # 1) Daño a enemigos
        hit_any = False
        for en in list(getattr(world, "enemies", [])):
            if not getattr(en, "alive", False):
                continue
            if hb.colliderect(en.rect):
                evt = DamageEvent(amount=self.damage,
                                  tags=self.out_tags,
                                  source=player,
                                  knockback=(self.knockback[0] * (1 if player.facing >= 0 else -1),
                                             self.knockback[1]))
                en.take_damage(evt)
                hit_any = True

        # 2) Reacciones del entorno (si existen)
        for rx in list(getattr(world, "reactives", [])):
            if not getattr(rx, "alive", False):
                continue
            if hb.colliderect(rx.rect):
                try:
                    rx.react(self.out_tags, source=player, world=world)
                    hit_any = True
                except Exception:
                    pass

        # (Opcional) feedback en el HUD/toast
        if hit_any and hasattr(world, "_show_mic_msg"):
            world._show_mic_msg("Golpe!")

        # Gasta energía y activa cooldown
        self.commit_use(player, now_ms)
        return True