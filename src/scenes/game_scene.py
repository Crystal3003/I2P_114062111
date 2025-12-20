import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, input_manager, scene_manager
from src.sprites import Sprite, Animation
from typing import override, Dict, Tuple
from src.interface.components.chat_overlay import ChatOverlay
from src.interface.components import Button, Slider, CheckBox
from src.entities.enemy_trainer import EnemyTrainer
from src.maps.minimap import MiniMap
from src.maps.map import Map
from src.maps.navigate import Navigator
from src.data.setting_menu import SettingsMenu
class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    backpack_button: Button
    setting_button: Button
    exit_button: Button
    save_button: Button
    load_button: Button
    _online_animations: dict[int, Animation]
    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        #Buttons
        px, py = GameSettings.SCREEN_WIDTH, 0
        self.center_x, self.center_y = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            px - 50, py, 50, 50,
            lambda: self.open_ui("backpack")
        )
        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px - 100, py, 50, 50,
            lambda: self.open_ui("settings")
        )
        self.navigation_button = Button(
            "UI/custom/navigation_button.png", "UI/custom/navigation_button_hover.png",
            px - 150, py, 50, 50,
            lambda: self.open_ui("navigation")
        )
        self.shopping = False
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            self._chat_overlay = ChatOverlay(
                send_callback = lambda text: self.online_manager.send_chat(text), # <- send chat method
                get_messages = lambda limit: self.online_manager.get_recent_chat(limit), # <- get chat messages method
            )
        else:
            self.online_manager = None
        self._chat_overlay = None
        self._online_animations = {}
        self._chat_bubbles: Dict[int, Tuple[str, str]] = {}
        self._last_chat_id_seen = 0
        self._online_last_pos = {}
        #texts
        font = pg.font.Font("assets/fonts/Minecraft.ttf",40)
        self.text_music = font.render("Music", 0, (0, 0, 0))
        self.text_settings = pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Settings", 0, (0, 0, 0))
        self.text_bag = pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Bag", 0, (0, 0, 0))
        self.text_navigation = pg.font.Font("assets/fonts/Minecraft.ttf", 60).render("Navigation", 0, (0, 0, 0))
        #minimap
        self.minimap = MiniMap(200, self.game_manager)
        #navigator
        goals = self.game_manager.current_navigate_points
        self.navigator = Navigator(self.game_manager, goals)
        self.navigator.generate_buttons()
        # settings
        self.setting_menu = SettingsMenu(self.game_manager)
    
    def open_ui(self, name: str):
        if name == "backpack":
            self.game_manager.bag.monster_menu.open()
            pass
        elif name == "navigation":
            self.navigator.menu.open()
        elif name == "settings":
            self.setting_menu.open()
    @override
    def enter(self) -> None:
        if sound_manager.current_bgm is None:
            sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
            self.online_manager.update(
                self.game_manager.player.position.x,
                self.game_manager.player.position.y,
                self.game_manager.current_map_key,
                self.game_manager.player.direction.name,
                self.game_manager.player.moving)
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()

    def navigator_auto_move(self, target):
        tx, ty = target
        dx = tx - self.game_manager.player.position.x
        dy = ty - self.game_manager.player.position.y

        if abs(dx) < 2 and abs(dy) < 2:
            return

        if abs(dx) > abs(dy):
            direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            direction = "DOWN" if dy > 0 else "UP"
        self.game_manager.player.moving_direction = direction
    
    @override
    def update(self, dt: float):
        NotOpeningSomething: bool = \
            not self.shopping and \
            not (self._chat_overlay and self._chat_overlay.is_open) and \
            not (self.game_manager.bag.monster_menu.active or self.game_manager.bag.item_menu.active) and \
            not self.navigator.menu.active and \
            not self.setting_menu.active
        
        # Check if there is assigned next scene
        if self.game_manager.try_switch_map():
            self.minimap.reload()
            self.navigator.goals = self.game_manager.current_navigate_points
            self.navigator.generate_buttons()

        # Update player and other data
        if (self.game_manager.player and 
            NotOpeningSomething) :
            self.game_manager.player.update(dt)
        # Update buttons
        if NotOpeningSomething:
            self.backpack_button.update(dt)
            self.setting_button.update(dt)
            self.navigation_button.update(dt)
        else:
            self.backpack_button.img_button = self.backpack_button.img_button_default
            self.setting_button.img_button = self.setting_button.img_button_default
            self.navigation_button.img_button = self.navigation_button.img_button_default
        # Update enter battle and shop
        # trainer
        # bush
        if self.game_manager.current_map.check_bush_detect(self.game_manager.player.rect) and input_manager.key_pressed(pg.K_SPACE) and NotOpeningSomething:
            scene_manager.change_scene("battle", game_manager=self.game_manager, bg_path="backgrounds/background1.png", battle_type='bush')
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            if NotOpeningSomething:
                enemy.enter_battle_update(dt)
        # shop
        for shop in self.game_manager.current_shops:
            shop.update(dt)
            if NotOpeningSomething:
                shop.enter_shop_update(dt)

        self.game_manager.bag.update(dt)
        # online manager
        if self.game_manager.player is not None and self.online_manager is not None:
            
            _ = self.online_manager.update(
                    self.game_manager.player.position.x,
                    self.game_manager.player.position.y,
                    self.game_manager.current_map_key,
                    self.game_manager.player.direction.name,
                    self.game_manager.player.moving
                )
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                pid = player["id"]
                if player["map"] == self.game_manager.current_map.path_name:
                    # online animation
                    if pid not in self._online_animations:
                        self._online_animations[pid] = Animation(
                            "character/ow1.png", ["down", "left", "right", "up"],
                            4, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                        )
                    anim = self._online_animations[pid]
                    if not player["moving"]:
                        anim.n_keyframes = 0
                    else:
                        anim.n_keyframes = 4
                    anim.update(dt)
                    # online pos
                    self._online_last_pos[pid] = (player["x"], player["y"])
                else:
                    self._online_last_pos.pop(pid, None)

        # Update ui
        self.setting_menu.update(dt)
        new_gm = self.setting_menu.poll_new_gm()
        if new_gm:
            self.game_manager = new_gm
            if self.game_manager.player: 
                self.game_manager.player.rect = self.game_manager.player.animation.rect.copy()
            self.game_manager.player.animation.update_pos(self.game_manager.player.position) 
            Logger.info("Game loaded")
        self.navigator.update(dt)
        target = self.navigator.get_next_pixel_target()
        if target:
            self.navigator_auto_move(target)
        else:
            self.game_manager.player.moving_direction = None
                              
        # shop
        for shop in self.game_manager.current_shops:
            if shop.shop_menu.active:
                self.shopping = True
            else:
                self.shopping = False
        # minimap
        self.minimap.update(dt)
        # chat overlay
        if self._chat_overlay:
            if input_manager.key_pressed(pg.K_t):
                self._chat_overlay.open()
            self._chat_overlay.update(dt)
        # Update chat bubbles from recent messages
        if self.online_manager:
            try:
                msgs = self.online_manager.get_recent_chat(50)
                max_id = self._last_chat_id_seen
                now = time.monotonic()
                for m in msgs:
                    mid = int(m.get("id", 0))
                    if mid <= self._last_chat_id_seen:
                        continue
                    sender = int(m.get("from", -1))
                    text = str(m.get("text", ""))
                    if sender >= 0 and text:
                        self._chat_bubbles[sender] = (text, now + 5.0)
                    if mid > max_id:
                        max_id = mid
                self._last_chat_id_seen = max_id
            except Exception:
                pass
        # debug
        DEBUG = False
        if DEBUG:
            print(self.game_manager.player.position.x // 64, self.game_manager.player.position.y // 64)

            
            
                
    @override
    def draw(self, screen: pg.Surface):      
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.navigator.draw_path(screen, camera)
            self.game_manager.player.draw(screen, camera)
            self.game_manager.current_map.draw_overlay(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        # UI
        self.backpack_button.draw(screen)
        self.setting_button.draw(screen)
        self.navigation_button.draw(screen)

        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        for shop in self.game_manager.current_shops:
            shop.draw(screen, camera)

        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    pid = player["id"]
                    try:
                        anim = self._online_animations[pid]
                        anim.update_pos(pos)
                        anim.switch(player["direction"].lower())
                        anim.draw(screen)
                    except:
                        pass
            try:
                self._draw_chat_bubbles(screen, camera)
            except Exception:
                pass
        # minimap
        self.minimap.draw(screen)

        self.game_manager.bag.draw(screen)
        self.navigator.draw(screen)
        self.setting_menu.draw(screen)

        if self._chat_overlay:
            self._chat_overlay.draw(screen)
    def _draw_chat_bubbles(self, screen: pg.Surface, camera: PositionCamera) -> None:
        if not self.online_manager:
            return
        # REMOVE EXPIRED BUBBLES
        now = time.monotonic()
        expired = [pid for pid, (_, ts) in self._chat_bubbles.items() if ts <= now]
        for pid in expired:
            self._chat_bubbles.pop(pid)
        if not self._chat_bubbles:
            return

        # DRAW LOCAL PLAYER'S BUBBLE
        font = pg.font.Font("assets/fonts/Pokemon Solid.ttf", 20)
        local_pid = self.online_manager.player_id
        if self.game_manager.player and local_pid in self._chat_bubbles:
            text, _ = self._chat_bubbles[local_pid]
            self._draw_chat_bubble_for_pos(screen, camera, self.game_manager.player.position, text, font)

        # DRAW OTHER PLAYERS' BUBBLES
        for pid, (text, _) in self._chat_bubbles.items():
            if pid == local_pid:
                continue
            pos_xy = self._online_last_pos.get(pid, None)
            if not pos_xy:
                continue
            px, py = pos_xy
            pos = Position(px, py)
            self._draw_chat_bubble_for_pos(screen, camera, pos, text, font)

    def _draw_chat_bubble_for_pos(self, screen: pg.Surface, camera: PositionCamera, world_pos: Position, text: str, font: pg.font.Font):
        word_limit = 20
        px, py = camera.transform_position(world_pos)
        px += GameSettings.TILE_SIZE / 2
        if len(text) > word_limit:
            text = text[:35] + "..."
        t = font.render(text, 0, (255, 255, 255))
        t_rect = t.get_rect()
        tw = t_rect.width
        th = t_rect.height
        px -= tw / 2
        py = py - th - 5

        bg = pg.Surface((tw + 10, th + 4), pg.SRCALPHA)
        bg.fill((0, 0, 0, 128))
        screen.blit(
            bg, (px - 5, py - 2)
        )
        screen.blit(
            t, (px, py)
        )
