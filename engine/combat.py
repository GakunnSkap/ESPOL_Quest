# engine/combat.py
from dataclasses import dataclass, field

class Team:
    PLAYER = "PLAYER"
    ENEMY = "ENEMY"
    ALLY = "ALLY"
    NEUTRAL = "NEUTRAL"


@dataclass
class DamageEvent:
    amount: int = 1
    tags: set = field(default_factory=set)
    source: object = None
    knockback: tuple = (0, 0)
    apply_status: list = field(default_factory=list)


def apply_damage(target, event: DamageEvent):
    """Aplica daño si el target tiene atributo 'hp'."""
    if not getattr(target, "alive", True):
        return
    dmg = getattr(event, "amount", 1)
    if hasattr(target, "hp"):
        target.hp -= dmg
        if target.hp <= 0:
            target.alive = False
