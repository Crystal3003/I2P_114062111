import pygame as pg
from src.interface.components import Button, TextedButton, GlowButton
from src.core.managers import GameManager
from src.utils.settings import GameSettings
from src.utils import Logger, ItemSprite
from src.sprites import Sprite
from src.data.bag import Bag
from src.utils.definition import Item, Monster
import math

class ShopMenu:
    deal_buttons: list[Button]
    sell_list: list
    buy_list: list
    def __init__(
            self,
            trade_table,
            game_manager: GameManager
            ) -> None:
        self.center_x = GameSettings.SCREEN_WIDTH // 2
        self.center_y = GameSettings.SCREEN_HEIGHT // 2
        self.active = False
        self.current_page = "buy"
        self.page = 1
        self.total_page = 1
        self.deal_buttons = []
        self.trade_table = trade_table
        self.buy_list = self.trade_table["buy"]
        self.sell_list = self.trade_table["sell"]
        self.trade_list = []
        self.sell_pokemons = self.trade_table["sell_pokemons"]
        self.game_manager = game_manager
        # buttons
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            GameSettings.SCREEN_WIDTH // 2 + 315, GameSettings.SCREEN_HEIGHT // 2 - 265, 50, 50,
            lambda: self.change_page("close")
        )
        self.buy_page_button = TextedButton(
            "Buy", 24,
            self.center_x - 220, self.center_y - 220,
            5,
            lambda: self.change_page("buy")
        )
        self.sell_page_button = TextedButton(
            "Sell", 24,
            self.center_x - 30 , self.center_y - 220,
            5,
            lambda: self.change_page("sell")
        )
        self.next_page_button = GlowButton(
            "UI/custom/UI_Flat_NextPage.png", 
            self.center_x + 355, self.center_y +240, 2,
            lambda: self.next_page("next")
        )
        self.previous_page_button = GlowButton(
            "UI/custom/UI_Flat_PreviousPage.png", 
            self.center_x + 275, self.center_y + 240, 2, 
            lambda: self.next_page("previous")
        )
    def next_page(self, method):
        if method == "next":
            self.page += 1
        elif method == "previous":
            self.page -= 1
    def change_page(self, page: str):
        if page == "close":
            Logger.info("Close shop")
            self.active = False
            return
        if self.current_page != page:
            self.current_page = page
            self.page = 1
            Logger.info(f"Change shop menu to {page}")
            self.generate_deal_buttons(self.buy_list.copy(), self.sell_list.copy())
    def generate_deal_buttons(self, buy_list: list, sell_list: list):
        self.trade_list = []
        self.trade_list = buy_list if self.current_page == "buy" else sell_list.copy()
        self.deal_buttons = []
        start_y = self.center_y - 130
        spacing = 90
        if self.current_page == "sell" and self.sell_pokemons["enabled"] == "True" and len(self.game_manager.bag._monsters_data) > 1:
            for p in self.game_manager.bag._monsters_data:
                item = p
                price = self.sell_pokemons["price"]
                self.trade_list.append({"item": item, "price": price})
                        
        for i, trade in enumerate(self.trade_list):
            if isinstance(trade["item"], dict):
                try:
                    trade["item"] = Monster(**trade["item"])
                except:
                    trade["item"] = Item(**trade["item"])
            else:
                pass # Trade is already Item of Monster
            if self.current_page == "buy":
                btn = Button(
                    "UI/button_shop.png", "UI/button_shop_hover.png",
                    self.center_x + 200, start_y + (i % 4) * spacing,
                    50, 50,
                    lambda t=trade: self.on_trade_click(t)
                )
                self.deal_buttons.append(btn)
            elif self.current_page == "sell":
                btn = Button(
                    "UI/custom/button_sell.png", "UI/custom/button_sell_hover.png",
                    self.center_x + 200, start_y + (i % 4) * spacing,
                    50, 50,
                    lambda t=trade: self.on_trade_click(t)
                )
                self.deal_buttons.append(btn)
    def on_trade_click(self, trade: dict):
        Logger.debug(f"clicked trade: {trade}")
        item = trade["item"]
        price = trade["price"]
        if self.current_page == "buy":
            coins = self.game_manager.bag.get_item_count("coins")
            if coins >= price:
                self.game_manager.bag.change_item_amount("coins", "add", -price)
                if isinstance(item, Item):
                    self.game_manager.bag.change_item_amount(item.id, "add", item.count)
                    Logger.info(f"Bought 1 {item}")
                if isinstance(item, Monster):
                    # Monster
                    self.game_manager.bag._monsters_data.append(item)
                    Logger.info(f"Bought a {item.name}")

        elif self.current_page == "sell":
            if isinstance(item, Item):
                count = self.game_manager.bag.get_item_count(item.id)
                if count > item.count:
                    self.game_manager.bag.change_item_amount("coins", "add", price)
                    self.game_manager.bag.change_item_amount(item.id, "add", -item.count)
            if isinstance(item, Monster):
                # Monster
                for monster in self.game_manager.bag._monsters_data:
                    if monster == item:
                        self.game_manager.bag._monsters_data.remove(monster)
                        self.game_manager.bag.change_item_amount("coins", "add", price)
                        self.generate_deal_buttons(self.buy_list.copy(), self.sell_list.copy())
                        break
    def update(self, dt: float):
        if self.active:
            self.exit_button.update(dt)
            self.buy_page_button.update(dt)
            self.sell_page_button.update(dt)
            start = (self.page - 1) * 4
            end = start + 4
            if end > len(self.deal_buttons) :
                end = len(self.deal_buttons)
            for btn in self.deal_buttons[start: end]:
                btn.update(dt)
            #
            self.total_page = math.ceil(len(self.deal_buttons) / 4)
            if self.page > 1:
                self.previous_page_button.update(dt)
            if self.page < self.total_page:
                self.next_page_button.update(dt)
            
    
    def draw(self, screen: pg.Surface):
        if self.active:
            frame = pg.image.load("assets/images/UI/raw/UI_Flat_Frame02a.png")
            frame = pg.transform.scale(frame,(800,600))
            px = GameSettings.SCREEN_WIDTH // 2 - frame.get_width() // 2
            py = GameSettings.SCREEN_HEIGHT // 2 - frame.get_height() // 2
            darken = pg.Surface((GameSettings.SCREEN_WIDTH,GameSettings.SCREEN_HEIGHT), flags = pg.SRCALPHA)
            darken.fill((0,0,0,128))
            title = pg.font.Font("assets/fonts/minecraft.ttf", 60).render("Shop", 0, (0, 0, 0))
            coin_img = Sprite("ingame_ui/coin.png", (30, 30))
            coin_count = pg.font.Font("assets/fonts/minecraft.ttf", 24).render(
                f"{self.game_manager.bag.get_item_count("coins")}", 0, (255, 255, 0))
            pages = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(
                f"{self.page} / {self.total_page}", 0, (255, 255, 255)
            )
            screen.blit(darken, (0, 0))
            screen.blit(frame, (px, py))
            screen.blit(title, (self.center_x - 370, self.center_y - 270))
            screen.blit(coin_img.image, (self.center_x + 200, self.center_y - 250))
            screen.blit(coin_count, (self.center_x + 250, self.center_y - 240))
            self.exit_button.draw(screen)
            self.buy_page_button.draw(screen)
            self.sell_page_button.draw(screen)
            
            if self.page > 1:
                self.previous_page_button.draw(screen)
            if self.page < self.total_page:
                self.next_page_button.draw(screen)
            screen.blit(pages, (self.center_x + 305, self.center_y + 245))

            start = (self.page - 1) * 4
            end = start + 4
            for btn in self.deal_buttons[start: end]:
                btn.draw(screen)
            start_y = self.center_y - 140
            spacing = 90
            item_frame = Sprite("UI/raw/UI_Flat_InputField01a.png", (480, 70))
            for i, b in enumerate(self.trade_list[start: end]):
                item = b["item"]
                price = b["price"]
                price_text = pg.font.Font("assets/fonts/minecraft.ttf", 24).render(
                    f"${price}", 0, (255, 255, 255)
                )
                screen.blit(price_text, (self.center_x + 260, start_y + 25 + i * spacing))
                if isinstance(item, Item):
                    name_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(
                        f"{item.name} x {item.count}", 0, (0, 0, 0)
                    )
                    img = Sprite(item.sprite_path, (30, 30))
                    count = self.game_manager.bag.get_item_count(item.id)
                    count_text = pg.font.Font("assets/fonts/minecraft.ttf", 14).render(
                        f"Owned: {count}", 0, (0, 0, 0)
                    )
                    screen.blit(item_frame.image, (self.center_x - 350, start_y + i * spacing))
                    screen.blit(img.image, (self.center_x - 310, start_y + i * spacing + 15))
                    screen.blit(name_text, (self.center_x - 250, start_y + i * spacing + 25))
                    screen.blit(count_text, (self.center_x + 25, start_y + i * spacing + 35))
                if isinstance(item, Monster):
                    # Monster / Pokemon
                    item.show_info(screen, self.center_x - 350, start_y + i * spacing)