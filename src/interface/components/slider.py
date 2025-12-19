from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager, sound_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent
from src.utils import GameSettings
class Slider(UIComponent):
    def __init__(
        self, x: int, y: int,
        width: int, height: int,
        image_path: str
    ):
        self.handle_size = height
        self.slider_rect = pg.Rect(x, y, width, height)
        self.slider_hitbox = pg.Rect(x - width, y + height, width + self.handle_size * 2, height + self.handle_size)
        self.handle_image = Sprite(image_path,(self.handle_size,self.handle_size))
        self.dragging_slider = False
        self.current_volume = GameSettings.AUDIO_VOLUME
        input_manager.handle_events
    @override
    def update(self, dt: float) -> None:
        if input_manager.mouse_down(1) and self.dragging_slider:
            rel_x = input_manager.mouse_pos[0] - self.slider_rect.x
            self.current_volume = max(0, min(1, rel_x / self.slider_rect.width))
            sound_manager.set_music_volume(self.current_volume)
        if input_manager.mouse_pressed(1):
            if self.slider_rect.collidepoint(input_manager.mouse_pos):
                self.dragging_slider = True
        if input_manager.mouse_released(1):
            self.dragging_slider = False
        self.handle_x = self.slider_rect.x + int(self.current_volume * self.slider_rect.width) - self.handle_size // 2
        self.handle_y = self.slider_rect.centery - self.handle_size // 2        
    @override
    def draw(self, screen: pg.Surface) -> None:
        pg.draw.rect(
        screen,
        (220, 220, 220),
        (self.slider_rect.x, self.slider_rect.centery - 10,
         self.slider_rect.width, 20)
    )
        

        screen.blit(self.handle_image.image, (self.handle_x, self.handle_y))