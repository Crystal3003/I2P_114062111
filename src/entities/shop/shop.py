from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from src.entities.entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera, Logger
from src.interface.components import Button, TextedButton
from .shop_menu import ShopMenu
class Shop(Entity):
    max_tiles: int | None
    warning_sign: Sprite
    detected: bool
    los_direction: Direction
    trade_table: dict
    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        anim_sprite_path: str,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
        trade_table: dict | None = None,
    ) -> None:
        super().__init__(x, y, game_manager, anim_sprite_path)
        self.max_tiles = max_tiles
        self._set_direction(facing)
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False
        self.trade_table = trade_table or {"buy": [], "sell": []}
        self.buy = self.trade_table["buy"]
        self.sell = self.trade_table["sell"]
        # shopping menu
        self.shop_menu = ShopMenu(self.trade_table, game_manager)

    @override
    def update(self, dt: float) -> None:
        self._has_los_to_player()
        self.animation.update_pos(self.position)
        self.shop_menu.update(dt)
    def enter_shop_update(self, dt):
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            self.shop_menu.active = True
            self.shop_menu.generate_deal_buttons(self.buy, self.sell)
            Logger.info("Enter shop")
    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)
        self.shop_menu.draw(screen)
    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:

        tile = GameSettings.TILE_SIZE
        size = tile * self.max_tiles

        if self.los_direction == Direction.UP:
            return pygame.Rect(self.position.x, self.position.y - size, tile, size)
        if self.los_direction == Direction.DOWN:
            return pygame.Rect(self.position.x, self.position.y + tile, tile, size)
        if self.los_direction == Direction.LEFT:
            return pygame.Rect(self.position.x - size, self.position.y, size, tile)
        if self.los_direction == Direction.RIGHT:
            return pygame.Rect(self.position.x + size, self.position.y, size, tile)
        return None

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
        player_rect = player.rect
        if los_rect.colliderect(player_rect):
            self.detected = True
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "Shop":
        max_tiles = data.get("max_tiles")
        anim = data.get("anim")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        trade_table = data.get("trade_table", {})
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            anim,
            max_tiles,
            facing,
            trade_table
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        base["trade_table"] = self.trade_table
        return base 