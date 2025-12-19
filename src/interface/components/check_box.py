from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class CheckBox(UIComponent):
    img_off: Sprite
    img_on: Sprite
    hitbox: pg.Rect
    on_func: Callable[[], None] | None

    def __init__(
        self,
        img_off: str, img_on:str,
        x: int, y: int, width: int, height: int, on = False,
        on_func: Callable[[], None] | None = None,
        off_func: Callable[[], None] | None = None,

    ):
        self.hitbox = pg.Rect(x, y, width, height)
        self.img_on = Sprite(img_on, (width, height))
        self.img_off = Sprite(img_off, (width, height))
        self.on_func = on_func
        self.off_func = off_func
        self.on = on
    @override
    def update(self, dt: float) -> None:
        if self.hitbox.collidepoint(input_manager.mouse_pos) and input_manager.mouse_pressed(1):
                if self.on:
                    self.on = False
                elif not self.on:
                    self.on = True
        if self.on:
            self.on_func()
        elif self.off_func is not None:
            self.off_func()
    @override
    def draw(self, screen: pg.Surface) -> None:
        if self.on:
            screen.blit(self.img_on.image, self.hitbox)
        elif not self.on:
            screen.blit(self.img_off.image, self.hitbox)