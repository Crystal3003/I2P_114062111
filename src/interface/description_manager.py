import pygame as pg
from src.utils.settings import GameSettings
from src.core.services import input_manager

class DescriptionManager:
    def __init__(self, font_path, font_size=16):
        self.font = pg.font.Font(font_path, font_size)
        self.descriptions = []
        self.hint = None
        # description block
        self.block = pg.Surface((GameSettings.SCREEN_WIDTH, 100), pg.SRCALPHA)
        self.block.fill((64, 64, 64, 255))

    def set(self, text_list):
        self.descriptions = [
            (self.font.render(t, True, (255, 255, 255)), t)
            for t in text_list
        ]
    def add(self, text, index=None):
        if index == None:
            self.descriptions.append((self.font.render(text, True, (255, 255, 255)), text))
        else:
            self.descriptions.insert((index, self.font.render(text, True, (255, 255, 255)),text))
    def replace(self, index, text):
        self.descriptions[index] = (self.font.render(text, True, (255, 255, 255)), text)
    def pop(self, index = -1):
        self.descriptions.pop(index)

    def set_hint(self, hint_font_path, text="press Space to continue...", size=16):
        font = pg.font.Font(hint_font_path, size)
        self.hint = font.render(text, True, (255, 229, 0))

    def update(self, dt):
        if self.descriptions and input_manager.key_pressed(pg.K_SPACE):
            self.descriptions.pop(0)

    def draw(self, screen: pg.Surface):
        screen.blit(self.block, (0, GameSettings.SCREEN_HEIGHT - 100))
        if self.descriptions:
            screen.blit(
                self.descriptions[0][0],
                (150, GameSettings.SCREEN_HEIGHT - 60),
            )
            if self.hint:
                screen.blit(
                    self.hint,
                    (GameSettings.SCREEN_WIDTH - 200, GameSettings.SCREEN_HEIGHT - 20),
                )