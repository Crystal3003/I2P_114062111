import pygame as pg
from src.interface.components import Menu, GlowButton
from src.utils.definition import Item
from src.core.services import input_manager
from src.utils.settings import GameSettings
from src.sprites import Sprite
from src.utils import draw_text_wrapped
from src.interface.components import Button
class ItemMenu:
    def __init__(
                 self,
                 _item_data: list[Item]):
        self.menu = Menu(items = _item_data, items_per_page = 6)
        self.info_block = pg.Surface((230, 445), pg.SRCALPHA)
        self.info_block.fill((100,100,100,200))
        self.current_info = None

        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2
        self.next_page_button = GlowButton(
            "UI/custom/UI_Flat_NextPage.png", 
            center_x + 355, center_y +240, 2,
            lambda: (self.menu.next_page(),self.on_page_change())
        )
        self.previous_page_button = GlowButton(
            "UI/custom/UI_Flat_PreviousPage.png", 
            center_x + 275, center_y + 240, 2, 
            lambda: (self.menu.prev_page(), self.on_page_change())
        )
        
        self.active = False
        self.active = False
        self.darken = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        self.darken.fill((0, 0, 0, 128))
        self.frame = pg.image.load("assets/images/UI/raw/UI_Flat_Frame03a.png")
        self.frame = pg.transform.scale(self.frame,(800,600))
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            center_x + 315, center_y - 265, 50, 50,
            lambda: self.close()
        )

    def close(self):
        self.active = False

    def open(self):
        self.active = True
    def on_page_change(self):
        pass
    def update(self, dt:float):
        if self.active:
            visible_item = self.menu.get_visible_items()
            visible_item: list[Item]
            self.current_info = None
            self.exit_button.update(dt)
            if input_manager.key_pressed(pg.K_ESCAPE):
                    self.close()
            if self.menu.page < self.menu.total_page:
                self.next_page_button.update(dt)
            if 1 < self.menu.page:
                self.previous_page_button.update(dt)
            for i, m in enumerate(visible_item):
                item_info_rect = pg.Rect(285, 155 + 80*i, 420, 70)
                if item_info_rect.collidepoint(input_manager.mouse_pos):
                    self.current_info = m
                    break
    def draw(self, screen: pg.Surface):
        if self.active:
            screen.blit(self.darken, (0, 0))
            px = GameSettings.SCREEN_WIDTH // 2 - self.frame.get_width() // 2
            py = GameSettings.SCREEN_HEIGHT // 2 - self.frame.get_height() // 2
            screen.blit(self.frame, (px, py))
            self.exit_button.draw(screen)
        
            visible_item = self.menu.get_visible_items()
            visible_item: list[Item]
            center_x = GameSettings.SCREEN_WIDTH // 2
            center_y = GameSettings.SCREEN_HEIGHT // 2
            if self.menu.page < self.menu.total_page:
                self.next_page_button.draw(screen)
            if 1 < self.menu.page:
                self.previous_page_button.draw(screen)
            pages = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(
                    f"{self.menu.page} / {self.menu.total_page}", 0, (255, 255, 255)
                )
            screen.blit(pages, (center_x + 305, center_y + 245))

            item_frame = Sprite("UI/raw/UI_Flat_InputField01a.png", (420, 70))
            for i, item in enumerate(visible_item):
                name_text = pg.font.Font("assets/fonts/minecraft.ttf", 20).render(
                    f"{item.name}", 0, (0, 0, 0)
                )
                count_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(
                    f"owned: {item.count}", 0, (0, 0, 0)
                )
                sprite = Sprite(item.sprite_path, (50, 50))
                screen.blit(item_frame.image, (285, 155 + 80*i))
                screen.blit(name_text, (360, 180 + 80*i))
                screen.blit(count_text, (550, 190 + 80*i))
                screen.blit(sprite.image, (300, 165 + 80*i ))
            if self.current_info:
                screen.blit(self.info_block, (770, 150))
                item = self.current_info
                lines = [
                    f"Name: {item.name}",
                ]
                for t in item.texts:
                    lines.append(t)
                rect = pg.Rect(780, 160, 210, 425)
                for line in lines:
                    draw_text_wrapped(
                        screen,
                        line,
                        pg.font.Font("assets/fonts/minecraft.ttf", 16),
                        (255,255,255),
                        rect
                    )
                    rect.y += 40
                pass # Item info
