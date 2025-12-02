# core/resources.py
import os
import pygame
from core.config import ASSETS_DIR, PLAYER_W, PLAYER_H, SPRITE_SMOOTHING, HUD_FONT_SMALL, HUD_FONT_BIG

_fonts = {}
_images = {}   # cache: (path, size) -> Surface
_initialized = False

def _ensure_init():
    global _initialized
    if _initialized:
        return
    _init_fonts()
    _initialized = True

def _init_fonts():
    _fonts["hud"]   = pygame.font.SysFont("consolas", HUD_FONT_SMALL)
    _fonts["debug"] = pygame.font.SysFont("consolas", HUD_FONT_SMALL-2)
    _fonts["big"]   = pygame.font.SysFont("consolas", HUD_FONT_BIG)

def load_fonts():
    _ensure_init()

def font(name="hud"):
    _ensure_init()
    return _fonts.get(name)

# ---------- IMÁGENES / ANIMACIONES ----------
def _key(path, size):
    return (path, size[0], size[1])

def load_image(rel_path: str, size=None) -> pygame.Surface:
    """
    Carga una imagen desde assets/ y la escala si 'size' (w,h) se indica.
    Usa caché para evitar recargas.
    """
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"[resources] No existe: {full_path}")

    key = _key(full_path, size or (-1, -1))
    if key in _images:
        return _images[key]

    img = pygame.image.load(full_path).convert_alpha()
    if size is not None:
        if SPRITE_SMOOTHING:
            img = pygame.transform.smoothscale(img, size)
        else:
            img = pygame.transform.scale(img, size)   # ⬅️ crisp para pixel-art
    _images[key] = img
    return img

def load_frames(dir_rel_path: str, size=None) -> list[pygame.Surface]:
    """
    Carga todos los archivos .png en un directorio dentro de assets/, ordenados por nombre.
    """
    full_dir = os.path.join(ASSETS_DIR, dir_rel_path)
    if not os.path.isdir(full_dir):
        raise FileNotFoundError(f"[resources] No es directorio: {full_dir}")
    names = [n for n in os.listdir(full_dir) if n.lower().endswith(".png")]
    names.sort()  # 0.png, 1.png, 2.png...
    return [load_image(os.path.join(dir_rel_path, n), size=size) for n in names]

# Helpers específicos del jugador
def load_player_idle():
    return load_image("player/idle.png", size=(PLAYER_W, PLAYER_H))

def load_player_run():
    return load_frames("player/run", size=(PLAYER_W, PLAYER_H))

