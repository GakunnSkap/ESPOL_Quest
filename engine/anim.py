# engine/anim.py
import pygame

class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: float=8.0, loop: bool=True):
        self.frames = frames or []
        self.fps = max(0.1, fps)
        self.loop = loop
        self.t = 0.0
        self.index = 0

    def reset(self):
        self.t = 0.0
        self.index = 0

    def update(self, dt: float):
        if len(self.frames) <= 1:
            return
        self.t += dt
        frame_time = 1.0 / self.fps
        while self.t >= frame_time:
            self.t -= frame_time
            self.index += 1
            if self.index >= len(self.frames):
                self.index = 0 if self.loop else len(self.frames) - 1

    def get(self) -> pygame.Surface | None:
        if not self.frames:
            return None
        return self.frames[self.index]
