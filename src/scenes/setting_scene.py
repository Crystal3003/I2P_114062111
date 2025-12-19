'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button, Slider, CheckBox, TextedButton
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class SettingScene(Scene):
    background: BackgroundSprite
    exit_button: Button
    volumn_slider: Slider
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.frame = pg.image.load("assets/images/UI/raw/UI_Flat_Frame03a.png")
        self.frame = pg.transform.scale(self.frame,(800,600))
        self.darken = pg.Surface((GameSettings.SCREEN_WIDTH,GameSettings.SCREEN_HEIGHT), flags = pg.SRCALPHA)
        self.darken.fill((0,0,0,128))
        self.center_x, self.center_y = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            self.center_x + 315, self.center_y - 265, 50, 50,
            lambda: scene_manager.change_scene("menu")
        )
        self.volumn_slider = Slider(
            self.center_x - 250, self.center_y - 70, 500, 20,
            "UI/raw/UI_Flat_Handle02a.png",
        )
        self.mute_check_box = CheckBox(
            "UI/raw/UI_Flat_ToggleOff03a.png", "UI/raw/UI_Flat_ToggleOn03a.png",
            self.center_x - 230, self.center_y + 10, 48, 27, True,
            lambda: self.unmute(),
            lambda: self.mute()
        )
        #test button
        self.test_button = TextedButton(
            "testing", 16,
            self.center_x + 400, self.center_y - 300, 5,
            lambda: scene_manager.change_scene("menu")
        )
        #texts
        font = pg.font.Font("assets/fonts/Minecraft.ttf",40)
        self.text_music = font.render("Music", 0, (0, 0, 0))
        self.text_settings = pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Settings", 0, (0, 0, 0))
    
    def mute(self) -> None:
        GameSettings.MUTED = True
        sound_manager.current_bgm.set_volume(0)
    def unmute(self) -> None:
        GameSettings.MUTED = False
        sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
    
    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_ESCAPE):
            scene_manager.change_scene("menu")
            return
        self.exit_button.update(dt)
        self.volumn_slider.update(dt)
        self.mute_check_box.update(dt)
        #texts
        if not GameSettings.MUTED and sound_manager.current_bgm is not None:
            volume_value = sound_manager.current_bgm.get_volume() * 100
            volume_str = f'{volume_value:.0f}%'
        else:
            volume_str = 'Muted'
        self.text_volume = pg.font.Font("assets/fonts/Minecraft.ttf",40).render(f"Volume: {volume_str}", 0, (0, 0, 0))
        self.test_button.update(dt)
    @override
    def draw(self, screen: pg.Surface) -> None:
        px = GameSettings.SCREEN_WIDTH // 2 - self.frame.get_width() // 2
        py = GameSettings.SCREEN_HEIGHT // 2 - self.frame.get_height() // 2
        self.background.draw(screen)
        screen.blit(self.darken, (0,0))
        screen.blit(self.frame, (px, py))
        self.exit_button.draw(screen)
        self.volumn_slider.draw(screen)
        self.mute_check_box.draw(screen)
        screen.blit(self.text_music, (self.center_x - 360, self.center_y + 5))
        screen.blit(self.text_volume, (self.center_x - 150, self.center_y - 150))
        screen.blit(self.text_settings, (self.center_x - 370, self.center_y - 270)) 
        self.test_button.draw(screen)