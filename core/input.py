# core/input.py
import pygame

KEYMAP = {
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "DOWN": pygame.K_s,
    "JUMP": pygame.K_SPACE,
    "ATTACK": pygame.K_j,
    "SKILL1": pygame.K_k,
    "SKILL2": pygame.K_l,
    "INTERACT": pygame.K_e,
    "DASH": pygame.K_LSHIFT,
    "POWER_PREV": pygame.K_q,
    "POWER_NEXT": pygame.K_r,
    "MAP": pygame.K_TAB,
    "MENU": pygame.K_ESCAPE,
}

def read_intents() -> dict:
    """Devuelve un diccionario de 'intents' booleanos para el frame actual."""
    keys = pygame.key.get_pressed()
    return {
        "move_left":  keys[KEYMAP["LEFT"]],
        "move_right": keys[KEYMAP["RIGHT"]],
        "move_down":  keys[KEYMAP["DOWN"]],
        "jump":       keys[KEYMAP["JUMP"]],
        "attack":     keys[KEYMAP["ATTACK"]],
        "skill1":     keys[KEYMAP["SKILL1"]],
        "skill2":     keys[KEYMAP["SKILL2"]],
        "interact":   keys[KEYMAP["INTERACT"]],
        "dash":       keys[KEYMAP["DASH"]],
        "power_prev": keys[KEYMAP["POWER_PREV"]],
        "power_next": keys[KEYMAP["POWER_NEXT"]],
        "open_map":   keys[KEYMAP["MAP"]],
        "open_menu":  keys[KEYMAP["MENU"]],
    }
