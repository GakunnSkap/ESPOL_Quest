# main.py
import sys, pygame
from core.config import VIRTUAL_W, VIRTUAL_H, FPS, FULLSCREEN, BORDERLESS, SCALE_MODE, LETTERBOX, MIC_DEVICE_INDEX, MIC_LANGUAGE
from core.scene import SceneManager
from levels.test_level import TestLevel
from core.resources import load_fonts
from core.voice import VoiceListener

WINDOW_TITLE = "ESPOL Quest — Beta"

class Game:
    def __init__(self):
        pygame.init()
        # Crear ventana según FULLSCREEN/BORDERLESS
        if FULLSCREEN:
            flags = pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((0, 0), flags)
        else:
            if BORDERLESS:
                # tamaño nativo del monitor (cubre incluso la barra)
                try:
                    desk_w, desk_h = pygame.display.get_desktop_sizes()[0]
                except Exception:
                    info = pygame.display.Info()
                    desk_w, desk_h = info.current_w, info.current_h
                self.screen = pygame.display.set_mode((desk_w, desk_h), pygame.NOFRAME)
            else:
                self.screen = pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)

        # canvas lógico donde el nivel dibuja el mundo
        self.canvas = pygame.Surface((VIRTUAL_W, VIRTUAL_H)).convert_alpha()

        load_fonts()
        self.manager = SceneManager(TestLevel(self))

        self.voice = VoiceListener(language=MIC_LANGUAGE, device_index=MIC_DEVICE_INDEX)
        self.voice.start()

        self.clock = pygame.time.Clock()
        self.running = True

    def _scale_rect(self, win_w, win_h):
        # calcula tamaño destino y offset según modo
        if SCALE_MODE == "pixel_crisp":
            # factor entero máximo
            scale = min(win_w // VIRTUAL_W, win_h // VIRTUAL_H)
            if scale < 1: scale = 1
            dst_w, dst_h = VIRTUAL_W * scale, VIRTUAL_H * scale
            ox = (win_w - dst_w) // 2 if LETTERBOX else 0
            oy = (win_h - dst_h) // 2 if LETTERBOX else 0
            return dst_w, dst_h, ox, oy, "nearest"

        if SCALE_MODE == "integer_smooth":
            scale = min(win_w // VIRTUAL_W, win_h // VIRTUAL_H)
            if scale >= 1:
                dst_w, dst_h = VIRTUAL_W * scale, VIRTUAL_H * scale
                ox = (win_w - dst_w) // 2 if LETTERBOX else 0
                oy = (win_h - dst_h) // 2 if LETTERBOX else 0
                return dst_w, dst_h, ox, oy, "smooth"
            # si no cabe entero, cae a smooth a pantalla completa con letterbox
            ratio = min(win_w / VIRTUAL_W, win_h / VIRTUAL_H)
            dst_w, dst_h = int(VIRTUAL_W * ratio), int(VIRTUAL_H * ratio)
            ox = (win_w - dst_w) // 2 if LETTERBOX else 0
            oy = (win_h - dst_h) // 2 if LETTERBOX else 0
            return dst_w, dst_h, ox, oy, "smooth"

        # smooth_only
        ratio = min(win_w / VIRTUAL_W, win_h / VIRTUAL_H)
        dst_w, dst_h = int(VIRTUAL_W * ratio), int(VIRTUAL_H * ratio)
        ox = (win_w - dst_w) // 2 if LETTERBOX else 0
        oy = (win_h - dst_h) // 2 if LETTERBOX else 0
        return dst_w, dst_h, ox, oy, "smooth"

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            if not self.manager.update(dt):
                self.running = False
                break
            self.manager.handle_events(events)

            # 1) dibuja mundo en canvas lógico
            self.canvas.fill((0,0,0,0))
            # << NUEVO: solo mundo, sin HUD >>
            if hasattr(self.manager.scene, "draw_world"):
                self.manager.scene.draw_world(self.canvas)
            else:
                self.manager.draw(self.canvas)  # fallback

            # 2) escala canvas al tamaño de la ventana
            win_w, win_h = self.screen.get_size()
            dst_w, dst_h, ox, oy, method = self._scale_rect(win_w, win_h)

            if method == "nearest":
                scaled = pygame.transform.scale(self.canvas, (dst_w, dst_h))
            else:
                scaled = pygame.transform.smoothscale(self.canvas, (dst_w, dst_h))

            # 3) limpia pantalla y blitea con letterbox
            self.screen.fill((0,0,0))
            self.screen.blit(scaled, (ox, oy))

            # 4) HUD “post-scale” (nítido 1:1 sobre la pantalla final)
            if hasattr(self.manager.scene, "draw_ui"):
                self.manager.scene.draw_ui(self.screen, (ox, oy, dst_w, dst_h))
            else:
                # fallback: si no existe draw_ui, que el nivel dibuje HUD normal
                self.manager.scene.hud.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        try: self.voice.stop()
        except Exception: pass
        sys.exit()



if __name__ == "__main__":
    Game().run()
