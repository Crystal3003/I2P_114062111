# src/interface/menus/settings_menu.py
import pygame as pg
from src.interface.components import BaseMenu
from src.interface.components import Button, Slider, CheckBox
from src.utils import GameSettings, Logger
from src.core.services import sound_manager
from src.core.managers import GameManager
from typing import override

class SettingsMenu(BaseMenu):
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager

        cx = GameSettings.SCREEN_WIDTH // 2
        cy = GameSettings.SCREEN_HEIGHT // 2

        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            cx + 315, cy - 265, 50, 50,
            self.close
        )

        self.volumn_slider = Slider(
            cx - 250, cy - 70, 500, 20,
            "UI/raw/UI_Flat_Handle02a.png",
        )

        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            cx - 365, cy + 165, 100, 100,
            lambda: self.game_manager.save("saves/game0.json")
        )

        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            cx - 145, cy + 165, 100, 100,
            lambda: self.load_save("saves/game0.json")
        )

        self.mute_check_box = CheckBox(
            "UI/raw/UI_Flat_ToggleOff03a.png", "UI/raw/UI_Flat_ToggleOn03a.png",
            cx - 230, cy + 10, 48, 27, False,
            lambda: self.unmute(),
            lambda: self.mute()
        )

        self.frame = pg.transform.scale(
            pg.image.load("assets/images/UI/raw/UI_Flat_Frame03a.png"),
            (800, 600)
        )

        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 60)
        self.font_text = pg.font.Font("assets/fonts/Minecraft.ttf", 40)
        self.text_volume = ""
        self._new_gm = None
    @override
    def open(self):
        super().open()
        self.volumn_slider.current_volume = GameSettings.AUDIO_VOLUME
        self.mute_check_box.on = not GameSettings.MUTED
    def load_save(self, path: str): 
        new_manager = GameManager.load(path) 
        if new_manager: 
            self._new_gm = new_manager
            Logger.info("Game loaded")

    def poll_new_gm(self):
        if self._new_gm:
            gm = self._new_gm
            self._new_gm = None
            return gm
        return None
    
    def mute(self):
        if sound_manager.current_bgm:
            sound_manager.current_bgm.set_volume(0)
        GameSettings.MUTED = True

    def unmute(self):
        if sound_manager.current_bgm:
            sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
        GameSettings.MUTED = False
    @override
    def update(self, dt):
        if not self.active:
            return
        self.exit_button.update(dt)
        self.volumn_slider.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.mute_check_box.update(dt)
        if not GameSettings.MUTED and sound_manager.current_bgm is not None: 
            volume_value = sound_manager.current_bgm.get_volume() * 100 
            volume_str = f'{volume_value:.0f}%' 
        else: 
            volume_str = 'Muted' 
        self.text_volume = pg.font.Font("assets/fonts/Minecraft.ttf",40).render(f"Volume: {volume_str}", 0, (0, 0, 0))
    @override
    def draw(self, screen: pg.Surface):
        if not self.active:
            return

        cx = GameSettings.SCREEN_WIDTH // 2
        cy = GameSettings.SCREEN_HEIGHT // 2
        px = cx - self.frame.get_width() // 2
        py = cy - self.frame.get_height() // 2
        font = pg.font.Font("assets/fonts/Minecraft.ttf",40)
        text_music = font.render("Music", 0, (0, 0, 0))
        darken = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        darken.fill((0, 0, 0, 128))
        screen.blit(darken, (0, 0))
        screen.blit(self.frame, (px, py))
        self.exit_button.draw(screen)
        self.volumn_slider.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.mute_check_box.draw(screen)

        screen.blit(text_music, (cx - 360, cy + 5)) 
        screen.blit(self.text_volume, (cx - 150, cy - 150))
        title = self.font_title.render("Settings", 0, (0, 0, 0))
        screen.blit(title, (cx - 370, cy - 270))
