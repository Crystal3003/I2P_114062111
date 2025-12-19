from .item_menu import ItemMenu, Item
from src.utils.definition import Monster, BattleMonster
from src.interface.components import Button, GlowButton
from src.utils import GameSettings, Logger
from typing import override
class BattleItemMenu(ItemMenu):
    btns: list[Button]
    def __init__(self, _item_data):
        super().__init__(_item_data)
        self.locked = False
        self.btns = []
        self._selected_item_id = None
    def generate_button(self):
        self.btns.clear()
        for i, item in enumerate(self.menu.get_visible_items()):
            item: Item
            for tag in item.tags:
                if tag == "in_battle":
                    btn = Button("UI/custom/use_button.png", "UI/custom/use_button_hover.png",
                                    GameSettings.SCREEN_WIDTH /2 , 170 + i*80,
                                    40, 40, lambda id=item.id: self.button_function(id))
                    self.btns.append(btn)
                    break

    def button_function(self, id: str):
        self._selected_item_id = id
        self.close()
        self.locked = False

    def poll_item_id(self):
        if self._selected_item_id is not None:
            item_id = self._selected_item_id
            self._selected_item_id = None
            return item_id
        return None
    def poll_exit(self):
        pass
    @override
    def on_page_change(self):
        super().on_page_change()
        self.generate_button()
    @override
    def open(self):
        super().open()
        self.generate_button()
    @override
    def update(self, dt):
        super().update(dt)
        self.exit_button.update(dt)
        for b in self.btns:
            b.update(dt)
    @override
    def exit_button_lock(self):
        if self.locked:
            return True
        return False
    @override
    def draw(self, screen):
        super().draw(screen)
        for b in self.btns:
            b.draw(screen)
