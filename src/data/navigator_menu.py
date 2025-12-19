import pygame as pg
from src.interface.components import Menu, GlowButton, TextedButton, Button
from src.maps.navigate_point import NavigatePoint
from src.core.services import input_manager
from src.utils.settings import GameSettings
from src.utils import Logger
class NavigatorMenu:
    btns: list[Button]
    def __init__(
                 self,
                 goals: list[NavigatePoint]):
        self.menu = Menu(items = goals, items_per_page = 12)

        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2
        self.next_page_button = GlowButton(
            "UI/custom/UI_Flat_NextPage.png", 
            center_x + 355, center_y +240, 2,
            lambda: (self.menu.next_page(), self.btns.clear())
        )
        self.previous_page_button = GlowButton(
            "UI/custom/UI_Flat_PreviousPage.png", 
            center_x + 275, center_y + 240, 2, 
            lambda: (self.menu.prev_page(), self.btns.clear())
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
        self.btns = []
        self.goals = goals
        self._selected_goal = None

    def close(self):
        self.active = False

    def open(self):
        self.active = True

    def generate_buttons(self):
        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2
        self.btns.clear()

        for i, goal in enumerate(self.menu.get_visible_items()):
            goal: NavigatePoint
            btn = TextedButton(
                goal.name, 24,
                center_x - 200 + (i % 2) * 200,
                center_y - 200 + (i // 2) * 100,
                5,
                lambda g=goal: self.on_click_event(g)
            )
            self.btns.append(btn)

        Logger.debug("Navigator buttons generated")

    def on_click_event(self, goal):
        self._selected_goal = goal
        self.close()
    def poll_result(self):
        if self._selected_goal:
            g = self._selected_goal
            self._selected_goal = None
            return g
        return None
    
    def update(self, dt:float):
        if not self.active:
            return
        
        if not self.btns:
            self.generate_buttons()

        self.exit_button.update(dt)
        for b in self.btns:
            b.update(dt)
        if self.menu.page < self.menu.total_page:
            self.next_page_button.update(dt)
        if 1 < self.menu.page:
            self.previous_page_button.update(dt)

    def draw(self, screen: pg.Surface):
        if not self.active:
            return

        screen.blit(self.darken, (0, 0))
        px = GameSettings.SCREEN_WIDTH // 2 - self.frame.get_width() // 2
        py = GameSettings.SCREEN_HEIGHT // 2 - self.frame.get_height() // 2
        screen.blit(self.frame, (px, py))
        self.exit_button.draw(screen)
    
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
        for b in self.btns:
            b.draw(screen)
        
        title =pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Navigator", 0, (0, 0, 0))
        screen.blit(title, (center_x - 370, center_y - 270))
