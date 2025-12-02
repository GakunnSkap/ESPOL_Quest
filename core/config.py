# core/config.py
VIRTUAL_W, VIRTUAL_H = 1920, 1080   # 16:9 virtual
FPS = 60

# Voz
MIC_DEVICE_INDEX = None
MIC_LANGUAGE = "es-ES"

# Ventana
FULLSCREEN  = False   
BORDERLESS  = True 
USE_SCALED = True          # escala la resolución lógica a la pantalla
# Escalado final
SCALE_MODE = "integer_smooth"   # "integer_smooth" | "smooth_only" | "pixel_crisp"
LETTERBOX  = True                # barras si no llena exacto


# Colores
COLOR_BG   = (12, 14, 18)
COLOR_HUD  = (200, 220, 255)
COLOR_TILE = (70, 90, 120)

# Física (tuning centralizado)
MOVE_SPEED      = 280        # px/s
JUMP_SPEED      = 520        # px/s
DASH_SPEED      = 580        # px/s
DASH_DURATION   = 0.18       # s
DASH_COOLDOWN   = 0.65       # s
GRAVITY         = 1400       # px/s^2
MAX_FALL_SPEED  = 900        # px/s

# (Opcional) Energía defaults (por si luego quieres leerlos desde aquí)
ENERGY_MAX      = 100.0
ENERGY_REGEN    = 12.0       # por segundo

#Sprites
ASSETS_DIR   = "assets"
PLAYER_W, PLAYER_H = 128, 128
DRAW_HITBOX  = False
SPRITE_SMOOTHING = False   # True = smoothscale, False = scale “crisp”

# HUD
HUD_FONT_SMALL = 20
HUD_FONT_BIG   = 24