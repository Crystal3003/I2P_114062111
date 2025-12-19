from __future__ import annotations
import pygame as pg
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.utils import GameSettings

"""
Elements:
Grass counter Water
Water counter Fire
Fire counter Grass
Dark counter All except Devine and Neutral
Devine counter Dark
None is None

Attributes:
Flying
"""

class Pokemon: # or known as Monster
    def __init__(self, name, hp, max_hp, level, sprite_path):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.level = level
        self.sprite_path = sprite_path
        self.img = Sprite(sprite_path, (150, 150))
        self.info_img = Sprite(sprite_path, (50, 50))
    
    def show_info(self, screen: pg.Surface, x, y, is_enemy: bool | None = False):
        if is_enemy:
            frame = Sprite("UI/custom/UI_Flat_Banner05a.png", (480, 70))
        else:
            frame = Sprite("UI/raw/UI_Flat_Banner04a.png", (480, 70))
        Name = pg.font.Font("assets/fonts/Minecraft.ttf", 14).render(f"{self.name}   Lv.{str(self.level)}", 0, (0, 0, 0))
        hp_ratio = self.hp / self.max_hp
        screen.blit(frame.image, (x, y))
        if is_enemy:
            screen.blit(self.info_img.image,  (x + 400, y + 10))
            Name_rect = Name.get_rect()
            screen.blit(Name, (x + 385 - Name_rect.width, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{self.hp} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 185, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 186 + 200 * (1 - hp_ratio), y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 95, y + 45))
        else:
            screen.blit(self.info_img.image,  (x + 30, y + 10))
            screen.blit(Name, (x + 95, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{self.hp} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 95, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 95, y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 305, y + 45))
    @classmethod
    def from_dict(cls, data: dict):
        pass
    
    def to_dict(self):
        pass
    @override
    def update(self, dt):
        pass
    @override
    def draw(self, screen):
        pass
