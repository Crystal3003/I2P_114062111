import pygame as pg
from src.utils import GameSettings
class BaseMenu:
    def __init__(self):
        self.active = False
    def open(self):
        self.active = True

    def close(self):
        self.active = False

    def update(self, dt: float):
        pass

    def draw(self, screen):
        pass
