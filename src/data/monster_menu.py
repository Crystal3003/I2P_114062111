import pygame as pg
from src.interface.components import Menu, GlowButton
from src.utils.definition import Monster
from src.core.services import input_manager
from src.utils.settings import GameSettings
from src.sprites import Sprite
from src.interface.components import Button
class MonsterMenu:
    def __init__(
                 self,
                 _monster_data: list[Monster]):
        self.menu = Menu(items = _monster_data, items_per_page = 6)
        self.info_block = pg.Surface((230, 445), pg.SRCALPHA)
        self.info_block.fill((100,100,100,200))
        self.current_info = None
        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2
        self.next_page_button = GlowButton(
            "UI/custom/UI_Flat_NextPage.png", 
            center_x + 355, center_y +240, 2,
            lambda: (self.menu.next_page(), self.on_page_change())
        )
        self.previous_page_button = GlowButton(
            "UI/custom/UI_Flat_PreviousPage.png", 
            center_x + 275, center_y + 240, 2, 
            lambda: (self.menu.prev_page(), self.on_page_change())
        )

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
    def exit_button_lock(self) -> bool:
        return False
    def update(self, dt:float):
        if self.active:
            visible_monster = self.menu.get_visible_items()
            visible_monster: list[Monster]
            self.current_info = None
            if not self.exit_button_lock():
                self.exit_button.update(dt)
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.close()
            if self.menu.page < self.menu.total_page:
                self.next_page_button.update(dt)
            if 1 < self.menu.page:
                self.previous_page_button.update(dt)
            for i, m in enumerate(visible_monster):
                monster_info_rect = pg.Rect(285, 155 + 80*i, 480, 70)
                if monster_info_rect.collidepoint(input_manager.mouse_pos):
                    self.current_info = m
                    break
    def draw(self, screen: pg.Surface):
        if self.active:
            screen.blit(self.darken, (0, 0))
            px = GameSettings.SCREEN_WIDTH // 2 - self.frame.get_width() // 2
            py = GameSettings.SCREEN_HEIGHT // 2 - self.frame.get_height() // 2
            screen.blit(self.frame, (px, py))
            if not self.exit_button_lock():
                self.exit_button.draw(screen)

            visible_monster = self.menu.get_visible_items()
            visible_monster: list[Monster]
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
            for i, m in enumerate(visible_monster):
                m.show_info(screen, 285, 155 + 80*i)
            if self.current_info:
                screen.blit(self.info_block, (770, 150))
                m = self.current_info
                lines = [
                    f"Name: {m.name}",
                    f"Level: {m.level}",
                    f"Exp: {m.exp} / {m.exp_to_next_level(m.level)}",
                    "",
                    f"Element: {m.element}",
                    f"HP: {m.hp} / {m.max_hp}",
                    f"ATK: {m.attack}",
                    f"DEF: {m.defense}",
                    f"SPD: {m.speed}",
                    "",
                    "Learned Skills:"
                ]
                for s in m.skill_set:
                    lines.append(f"  - {s.name}")
                for i, line in enumerate(lines):
                    text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(line, True, (255,255,255))
                    screen.blit(text, (780, 160 + i*20))
