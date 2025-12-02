# entities/player.py
import pygame
from engine.entity import Entity
from engine.physics import apply_gravity, move_and_collide
from engine.combat import Team
from engine.powers import EnergyPool, SimpleShotPower
from core.config import MOVE_SPEED, JUMP_SPEED, DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, PLAYER_W, PLAYER_H, DRAW_HITBOX
from core import resources
from engine.anim import Animation


class Player(Entity):
    # Colores de feedback (evita literales repetidos)
    COLOR_NORMAL = (230, 245, 255)
    COLOR_DASH   = (255, 200, 220)
    COLOR_HURT   = (255, 160, 160)

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_W, PLAYER_H, color=self.COLOR_NORMAL)
        self.team = Team.PLAYER
        self.use_gravity = True
        self.on_ground = False
        self.facing = 1

        # Vida / energía
        self.max_hp = 6
        self.hp = self.max_hp

        # Dash
        self.is_dashing = False
        self.dash_time = 0.0
        self.dash_cd_left = 0.0

        # Disparo básico (placeholder)
        self.shoot_cd_ms = 220
        self.last_shot_ms = -9999

        # Estado de daño (invulnerabilidad corta)
        self.hurt_timer = 0.0

        # Energía y poderes
        self.energy_pool = EnergyPool(max_energy=100, regen_rate=12)

        # Inventario por nombre (para voz)
        self.power_registry = {}   # name -> Power
        self.unlocked = set()      # nombres habilitados
        self._register_default_powers()

        #Sprite
        idle_img = resources.load_player_idle()
        run_frames = resources.load_player_run()

        self.anim_idle = Animation([idle_img], fps=1, loop=True)   # 1 frame
        self.anim_run  = Animation(run_frames, fps=10, loop=True)  # 4 frames @ 10 fps
        self._current_anim = self.anim_idle

    # ----------------- Helpers internos -----------------
    def _update_timers(self, dt: float):
        # clamp a 0 sin ramificaciones
        self.hurt_timer   = max(0.0, self.hurt_timer - dt)
        self.dash_cd_left = max(0.0, self.dash_cd_left - dt)
        # energía
        self.energy_pool.regen(dt)

    def _handle_move_jump(self, intents, dt: float):
        """WASD/espacio → movimiento y salto (sin cambiar comportamiento actual)."""
        if self.is_dashing:
            return  # Durante dash se ignora input de movimiento

        vx = 0
        if intents.get("move_left"):
            vx = -MOVE_SPEED
            self.facing = -1
        if intents.get("move_right"):
            vx = MOVE_SPEED
            self.facing = 1

        self.vel.x = vx

        # salto
        if intents.get("jump") and self.on_ground:
            self.vel.y = -JUMP_SPEED
            self.on_ground = False

    def _try_dash(self, intents):
        """Inicia dash si está disponible; cooldown se aplica al terminar (como antes)."""
        if self.is_dashing or self.dash_cd_left > 0.0:
            return
        if intents.get("dash"):
            self.is_dashing = True
            self.dash_time = DASH_DURATION
            # reset vertical para sensación más responsiva
            self.vel.y = 0
            self.vel.x = (self.facing if self.facing != 0 else 1) * DASH_SPEED

    # ----------------- Daño / estados -----------------
    def take_damage(self, amount=1):
        # invulnerabilidad simple por 0.4s tras recibir golpe (igual que antes)
        if self.hurt_timer > 0:
            return
        self.hp -= amount
        self.hurt_timer = 0.4
        if self.hp <= 0:
            self.alive = False

    # ----------------- Ciclo principal -----------------
    def update(self, dt, world):
        tiles = getattr(world, "tiles", [])

        # timers + energía
        self._update_timers(dt)

        # input → movimiento / dash
        intents = getattr(self, "intents", {})  # robusto por si no fue seteado
        self._handle_move_jump(intents, dt)
        self._try_dash(intents)

        # actualizar dash
        if self.is_dashing:
            self.dash_time -= dt
            if self.dash_time <= 0:
                self.is_dashing = False
                self.dash_cd_left = DASH_COOLDOWN
                # freno lateral al terminar dash para no “patinar”
                self.vel.x = 0

        # física
        apply_gravity(self, dt)
        move_and_collide(self, tiles, dt)

        self._select_anim()
        self._current_anim.update(dt)


    def draw(self, screen):
        # 1) imagen
        surf = self._current_anim.get()
        if surf:
            # flip horizontal según facing
            draw_img = pygame.transform.flip(surf, self.facing < 0, False)
            # alinear por topleft del rect de colisión
            screen.blit(draw_img, self.rect.topleft)
        else:
            # fallback si no hay sprite
            pygame.draw.rect(screen, self.color, self.rect)

        # 2) (opcional) mostrar hitbox
        if DRAW_HITBOX:
            pygame.draw.rect(screen, (0,255,0), self.rect, 1)


    # ===== Disparo básico (cooldown y punto de salida) =====
    def can_shoot(self, now_ms):
        return (now_ms - self.last_shot_ms) >= self.shoot_cd_ms

    def mark_shot(self, now_ms):
        self.last_shot_ms = now_ms

    def muzzle_pos(self):
        """Punto de salida de la bala según orientación."""
        if self.facing >= 0:
            return (self.rect.right, self.rect.centery)
        else:
            return (self.rect.left, self.rect.centery)

    # ----------------- Poderes por voz -----------------
    def _register_default_powers(self):
        reg = self.power_registry
        from engine.powers import MeleePower
        reg["golpe"] = MeleePower("golpe", energy_cost=0, cooldown_ms=280, damage=100,out_tags={"melee"})
        reg["rayo"]       = SimpleShotPower("rayo",       color=(255, 220, 80),energy_cost=8,cooldown_ms=150,out_tags={"electric"})
        reg["pulso"]      = SimpleShotPower("pulso",      color=(120,220,255), energy_cost=16, cooldown_ms=1200, out_tags={"emp"})
        reg["ralentizar"] = SimpleShotPower("ralentizar", color=(180,220,255), energy_cost=18, cooldown_ms=1400, out_tags={"time"})
        reg["congelar"]   = SimpleShotPower("congelar",   color=(160,240,255), energy_cost=20, cooldown_ms=1600, out_tags={"freeze"})
        reg["remache"]    = SimpleShotPower("remache",    color=(200,200,200), energy_cost=10, cooldown_ms=700,  out_tags={"metal"})
        reg["robot"]      = SimpleShotPower("robot",      color=(255,200,120), energy_cost=24, cooldown_ms=2200, out_tags={"summon"})
        reg["control"]    = SimpleShotPower("control",    color=(255,160,240), energy_cost=22, cooldown_ms=2500, out_tags={"mind"})
        reg["posesion"]   = SimpleShotPower("posesion",   color=(255,120,220), energy_cost=26, cooldown_ms=3000, out_tags={"possess"})
        reg["curar"]      = SimpleShotPower("curar",      color=(120,255,120), energy_cost=14, cooldown_ms=1800, out_tags={"heal"})
        reg["quimica"]    = SimpleShotPower("quimica",    color=(120,255,180), energy_cost=16, cooldown_ms=1600, out_tags={"chem"})
        reg["fuerza"]     = SimpleShotPower("fuerza",     color=(240,200,120), energy_cost=12, cooldown_ms=900,  out_tags={"force"})
        reg["sismo"]      = SimpleShotPower("sismo",      color=(255,140,80),  energy_cost=18, cooldown_ms=1800, out_tags={"quake"})
        reg["latigo"]     = SimpleShotPower("latigo",     color=(120,180,255), energy_cost=12, cooldown_ms=200,  out_tags={"water"})
        reg["burbuja"]    = SimpleShotPower("burbuja",    color=(100,200,255), energy_cost=20, cooldown_ms=2200, out_tags={"shield"})
        reg["pincel"]     = SimpleShotPower("pincel",     color=(255,200,255), energy_cost=10, cooldown_ms=800,  out_tags={"paint"})
        reg["revelar"]    = SimpleShotPower("revelar",    color=(255,255,160), energy_cost=16, cooldown_ms=1500, out_tags={"reveal"})
        self.unlock_power("golpe")
        self.unlock_power("rayo")
        self.unlock_power("latigo")

    def unlock_power(self, name: str):
        name = name.lower()
        if name in self.power_registry:
            self.unlocked.add(name)

    def has_power(self, name: str) -> bool:
        return name.lower() in self.unlocked

    def try_power_by_name(self, name: str, world) -> bool:
        name = name.lower()
        if name not in self.unlocked:
            return False
        p = self.power_registry.get(name)
        if not p:
            return False
        now = pygame.time.get_ticks()
        if not p.can_use(self, world, now):
            return False
        return p.use(self, world, now)
    
    def _select_anim(self):
        # prioridades simples: dash > moverse > idle
        if self.is_dashing:
            # mientras no tengamos anim de dash, usa run (rápida) como placeholder
            self._current_anim = self.anim_run
        else:
            moving = abs(self.vel.x) > 1e-3
            self._current_anim = self.anim_run if moving else self.anim_idle
