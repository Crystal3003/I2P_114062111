from __future__ import annotations
import pygame as pg


from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class GlowButton(UIComponent):
    img_button: Sprite
    img_button_default: Sprite
    hitbox: pg.Rect
    on_click: Callable[[], None] | None

    def __init__(self, sprite_path, x, y, scale, on_click=None):
        self.hovering = False

        self.img_button_default = Sprite(sprite_path)

        w = self.img_button_default.image.get_width()
        h = self.img_button_default.image.get_height()

        self.img_button = Sprite(sprite_path, (w * scale, h * scale))

        self.hitbox = pg.Rect(x, y, w * scale, h * scale)

        self.on_click = on_click

        self.glow_surface = self._generate_glow_surface(spread=4)
        self.glow_offset = (-4, -4)
    def _generate_glow_surface(self, spread: int = 4) -> pg.Surface:
        """Generate an outline glow based on alpha mask."""
        img = self.img_button.image
        w, h = img.get_size()

        glow = pg.Surface((w + spread*2, h + spread*2), pg.SRCALPHA)

        for y in range(h):
            for x in range(w):
                if img.get_at((x, y)).a > 0:  
                    pg.draw.circle(glow, (255, 255, 0, 255), 
                                (x + spread, y + spread), spread)

        return glow
    @override
    def update(self, dt: float) -> None:
        if self.hitbox.collidepoint(input_manager.mouse_pos):
            self.hovering = True
            if input_manager.mouse_pressed(1) and self.on_click is not None:
                self.on_click()
        else:
            self.hovering = False
    
    @override
    def draw(self, screen: pg.Surface) -> None:
        if self.hovering:
            screen.blit(self.glow_surface, 
                        (self.hitbox.x + self.glow_offset[0],
                        self.hitbox.y + self.glow_offset[1]))

        screen.blit(self.img_button.image, self.hitbox)