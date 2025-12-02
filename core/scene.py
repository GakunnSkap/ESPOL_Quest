# core/scene.py
import pygame

class Scene:
    def __init__(self, game):
        self.game = game
        self.next_scene = None
        self.quit_requested = False

    def handle_events(self, events): pass
    def update(self, dt: float): pass
    def draw(self, screen: pygame.Surface): pass

class SceneManager:
    def __init__(self, start_scene: Scene):
        self.scene = start_scene

    def handle_events(self, events):
        self.scene.handle_events(events)

    def update(self, dt):
        self.scene.update(dt)
        if self.scene.quit_requested:
            return False
        if self.scene.next_scene is not None:
            self.scene = self.scene.next_scene
        return True

    def draw(self, screen):
        self.scene.draw(screen)
