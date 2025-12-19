import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.sprites import Sprite
from src.utils import ItemSprite
from .monster_menu import MonsterMenu
from .item_menu import ItemMenu
from src.interface.components import TextedButton
class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []
        self.monster_menu = MonsterMenu(self._monsters_data)
        self.item_menu = ItemMenu(self._items_data)
        self.monster_page_button = TextedButton("Monster", 24,
                                                GameSettings.SCREEN_WIDTH // 2 - 200, GameSettings.SCREEN_HEIGHT // 2 - 260,
                                                5, lambda: self.change_page("monster"))
        self.item_page_button = TextedButton("Item", 24,
                                                GameSettings.SCREEN_WIDTH // 2 - 10, GameSettings.SCREEN_HEIGHT // 2 - 260,
                                                5, lambda: self.change_page("item"))
        self.monster_menu.close()
        self.item_menu.close()
    def change_page(self, page_name):
        if page_name == "monster":
            self.monster_menu.open()
            self.item_menu.close()
        elif page_name == "item":
            self.monster_menu.close()
            self.item_menu.open()

    def update(self, dt: float):
        self.monster_menu.update(dt)
        self.item_menu.update(dt)
        self.item_page_button.update(dt)
        self.monster_page_button.update(dt)

    def draw(self, screen: pg.Surface):
        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2
        texts = pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Bag", 0, (0, 0, 0))
        self.monster_menu.draw(screen)
        self.item_menu.draw(screen)
        if self.monster_menu.active or self.item_menu.active:
            self.monster_page_button.draw(screen)
            self.item_page_button.draw(screen)
            screen.blit(texts, (center_x - 370, center_y - 270))

    def get_item_count(self, id):
        for item in self._items_data:
            if item.id == id:
                return item.count
        return 0
    
    def change_item_amount(self, item_id, method, amount):
        target = None
        for item in self._items_data:
            if item.id == item_id:
                target = item
                break
        if target == None:
            target = Item(id=item_id, count=0)
            self._items_data.append(target)
        if method == "add":
            target.count += amount
        elif method == "write":
            target.count = amount

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": [m.to_dict() for m in self._monsters_data],
            "items": [i.to_dict() for i in self._items_data]
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = []
        try:
            for m in data.get("monsters"):
                monsters.append(Monster(**m))
        except:
            monsters = []
        items = []
        try:
            for i in data.get("items"):
                items.append(Item(**i))
        except:
            items = []
        bag = cls(monsters, items)
        return bag