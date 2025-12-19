from __future__ import annotations
import pygame as pg


from src.sprites import Sprite
from src.core.services import input_manager
from src.utils import Logger
from typing import Callable, override
from .component import UIComponent

class TextedButton(UIComponent):
    img_button: Sprite
    img_button_default: Sprite
    hitbox: pg.Rect
    on_click: Callable[[], None] | None

    def __init__(
        self,
        text: str, size: int,
        x: int, y: int, scale: int,
        on_click: Callable[[], None] | None = None,
    ):
        self.hovering = False
        width = 32 * scale
        height = 8 * scale
        self.img_button_default = Sprite("UI/raw/UI_Flat_Bar01a.png", (width, height))
        self.hitbox = pg.Rect(x, y, width, height)
        self.img_button = Sprite("UI/raw/UI_Flat_Bar01a.png", (width, height))      
        self.on_click = on_click
        self.text = pg.font.Font("assets/fonts/Minecraft.ttf", size).render(text, 0, (0, 0, 0))
        text_rect = self.text.get_rect(center=self.hitbox.center)
        self.text_x = text_rect.x
        self.text_y = text_rect.y
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
        _ = screen.blit(self.img_button.image, self.hitbox)
        screen.blit(self.text, (self.text_x, self.text_y))
        if self.hovering:
            pg.draw.rect(screen, (255, 255, 0), self.hitbox, 1)
def main():
    import sys
    import os
    
    pg.init()

    WIDTH, HEIGHT = 800, 800
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Button Test")
    clock = pg.time.Clock()
    
    bg_color = (0, 0, 0)
    def on_button_click():
        nonlocal bg_color
        if bg_color == (0, 0, 0):
            bg_color = (255, 255, 255)
        else:
            bg_color = (0, 0, 0)
        
    button = TextedButton(
        img_path="UI/button_play.png",
        img_hovered_path="UI/button_play_hover.png",
        x=WIDTH // 2 - 50,
        y=HEIGHT // 2 - 50,
        width=100,
        height=100,
        on_click=on_button_click
    )
    
    running = True
    dt = 0
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            input_manager.handle_events(event)
        
        dt = clock.tick(60) / 1000.0
        button.update(dt)
        
        input_manager.reset()
        
        _ = screen.fill(bg_color)
        
        button.draw(screen)
        
        pg.display.flip()
    
    pg.quit()


if __name__ == "__main__":
    main()
