# levels/level_base.py
import pygame
from core.scene import Scene
from core.input import read_intents
from entities.player import Player
from entities.enemy import EnemyBase
from engine.ui import HUD
from core.voice_commands import VOICE_TO_POWER
from collections import deque
from core.config import COLOR_BG, COLOR_TILE


class LevelBase(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = COLOR_BG
        self.tiles = []
        self.player = Player(80, 420)
        self.enemies = []
        self.bullets = []
        self.hud = HUD(self.player, self)
        self.boss = None
        self.miniboss = None
        self.mic_msg = ""
        self.mic_msg_timer = 0.0
        self.voice_cast_queue = deque()

    def add_tile(self, x, y, w, h):
        self.tiles.append(pygame.Rect(x, y, w, h))

    def spawn_enemy(self, x, y):
        self.enemies.append(EnemyBase(x, y))

    def update(self, dt):
        intents = read_intents()
        self.player.intents = intents
        self.player.update(dt, self)

        # --- VOZ: leer frases, mostrar SIEMPRE y encolar ráfagas ---
        if hasattr(self.game, "voice") and self.game.voice:
            for phrase in self.game.voice.get_commands():
                print(f"[VOICE] → {phrase}")
                self._show_mic_msg(phrase)  # siempre mostrar lo dicho

                words = phrase.lower().split()
                if not words:
                    continue

                now = pygame.time.get_ticks()
                offset = 0
                for word in words:
                    name = self._map_voice_to_power(word)
                    if not name:
                        continue
                    p = self.player.power_registry.get(name)
                    gap = max(80, (p.cooldown_ms if p else 0))  # 80 ms mínimo
                    due = now + offset
                    self.voice_cast_queue.append((due, name))
                    offset += gap

        # --- Procesar la cola de ráfagas (una vez por frame) ---
        now = pygame.time.get_ticks()
        while self.voice_cast_queue and self.voice_cast_queue[0][0] <= now:
            _, name = self.voice_cast_queue.popleft()
            self.player.try_power_by_name(name, self)  # si no está disponible: no hace nada

        # --- Balas ---
        for b in list(self.bullets):
            b.update(dt, self)
            if not b.alive:
                self.bullets.remove(b)

        # --- Enemigos ---
        for e in list(self.enemies):
            e.update(dt, self)
            if not e.alive:
                self.enemies.remove(e)

        # --- Respawn seguro (sin número mágico 540) ---
        screen_h = self.game.screen.get_height()
        if self.player.rect.top > screen_h + 200:
            self.player.rect.topleft = (80, 420)
            self.player.vel.xy = (0, 0)

        # --- Mensaje micrófono ---
        if self.mic_msg_timer > 0:
            self.mic_msg_timer -= dt
            if self.mic_msg_timer < 0:
                self.mic_msg_timer = 0

    def draw_world(self, screen):
        # Fondo
        screen.fill(self.bg_color)
        # Tiles
        for t in self.tiles:
            pygame.draw.rect(screen, COLOR_TILE, t)
        # Enemigos y balas
        for e in self.enemies: e.draw(screen)
        for b in self.bullets: b.draw(screen)
        # Jugador
        self.player.draw(screen)

    def draw_ui(self, screen, dst_rect=None):
        # HUD sobre pantalla final (nítido)
        self.hud.draw(screen)

        # Barras superiores
        if self.miniboss and getattr(self.miniboss, "alive", False):
            self.hud.draw_boss_bar(screen, self.miniboss, title="MINI JEFE")
        if self.boss and getattr(self.boss, "alive", False):
            self.hud.draw_boss_bar(screen, self.boss, title="JEFE")

        # Mensaje de mic (toast abajo)
        if self.mic_msg_timer > 0:
            font = pygame.font.SysFont("consolas", 18)
            surf = font.render(self.mic_msg, True, (220, 240, 255))
            x = (screen.get_width() - surf.get_width()) // 2
            y = int(screen.get_height() - 36)
            bg = pygame.Surface((surf.get_width()+16, surf.get_height()+8), pygame.SRCALPHA)
            bg.fill((20, 30, 50, 150))
            screen.blit(bg, (x-8, y-4))
            screen.blit(surf, (x, y))

    # Compatibilidad: draw llama a ambos en la misma surface
    def draw(self, screen):
        self.draw_world(screen)
        self.draw_ui(screen)
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F10:
                    if hasattr(self.game, "voice") and self.game.voice:
                        idx, name = self.game.voice.next_device()
                        self._show_mic_msg(f"Mic ↑: [{idx}] {name}")
                if e.key == pygame.K_F11:
                    if hasattr(self.game, "voice") and self.game.voice:
                        idx, name = self.game.voice.prev_device()
                        self._show_mic_msg(f"Mic ↓: [{idx}] {name}")
                if e.key == pygame.K_F9:  # re-escanear dispositivos
                    if hasattr(self.game, "voice") and self.game.voice:
                        self.game.voice.refresh_devices()
                        idx, name = self.game.voice.current_device()
                        self._show_mic_msg(f"Mic scan: [{idx}] {name}")

    def _show_mic_msg(self, text):
        self.mic_msg = text
        self.mic_msg_timer = 2.0

    def _map_voice_to_power(self, phrase: str):
        s = phrase.lower().strip()
        if s in VOICE_TO_POWER:
            return VOICE_TO_POWER[s]
        for key, val in VOICE_TO_POWER.items():
            if key in s:
                return val
        return None