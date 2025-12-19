from .monster_menu import MonsterMenu
from src.utils.definition import Monster, BattleMonster
from src.interface.components import Button, GlowButton
from src.utils import GameSettings, Logger
from typing import override
class BattleMonsterMenu(MonsterMenu):
    btns: list[Button]
    def __init__(self, _monster_data, current_monster: BattleMonster):
        super().__init__(_monster_data)
        self.locked = False
        self.current_monster = current_monster
        self.btns = []
        # Since monster data is a list, I use index to track the switch to avoid copy
        self._selected_monster_index = None
    def generate_button(self):
        self.btns.clear()
        for i, monster in enumerate(self.menu.get_visible_items()):
            monster: Monster
            if self.current_monster and self.current_monster.base == monster:
                continue # Same Monster
            elif monster.hp > 0:
                btn = Button("UI/custom/switch_button.png", "UI/custom/switch_button_hover.png",
                                 GameSettings.SCREEN_WIDTH /2 + 50, 170 + i*80,
                                 40, 40, lambda index = i: self.button_function(index))
                self.btns.append(btn)

    def button_function(self, index: int):
        self._selected_monster_index = index + (self.menu.page - 1) * 6
        self.close()
        self.locked = False

    def poll_monster_index(self):
        if self._selected_monster_index is not None:
            index = self._selected_monster_index
            self._selected_monster_index = None
            return index
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
        if self.locked:
            Logger.debug("BattleMonsterMenu opened in LOCKED mode")
    @override
    def update(self, dt):
        super().update(dt)
        if not self.locked:
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
