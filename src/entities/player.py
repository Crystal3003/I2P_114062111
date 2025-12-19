from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager, anim_sprite_path: str) -> None:
        player_anim_sprite = anim_sprite_path
        super().__init__(x, y, game_manager, player_anim_sprite)
        self.moving = False
        self.moving_direction = None
    @staticmethod
    def snap_to_grid(value: float) -> int:
        return round(value / GameSettings.TILE_SIZE) * GameSettings.TILE_SIZE

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        self.moving = False
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a) or self.moving_direction == "LEFT":
            dis.x -= self.speed * dt
            self.direction = Direction.LEFT
            self.moving = True
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d) or self.moving_direction == "RIGHT":
            dis.x += self.speed * dt
            self.direction = Direction.RIGHT
            self.moving = True
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s) or self.moving_direction == "DOWN":
            dis.y += self.speed * dt
            self.direction = Direction.DOWN
            self.moving = True
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w) or self.moving_direction == "UP":
            dis.y -= self.speed * dt
            self.direction = Direction.UP
            self.moving = True

        if dis.x != 0 and dis.y != 0:
            dis.x /= math.sqrt(2)
            dis.y /= math.sqrt(2)
        self.rect = self.animation.rect.copy()
        self.rect.x += dis.x
        if self.game_manager.check_collision(self.rect):
            self.rect.x -= dis.x
            self.rect.x = Entity._snap_to_grid(self.rect.x)
        self.rect.y += dis.y
        if self.game_manager.check_collision(self.rect):
            self.rect.y -= dis.y
            self.rect.y = Entity._snap_to_grid(self.rect.y)
            
        self.position.x = self.rect.x
        self.position.y = self.rect.y

        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.rect)
        if tp:
            dest = tp.destination
            dest_pos = tp.dest_pos
            self.game_manager.switch_map(dest, dest_pos)
        # update animation
        if not self.moving:
            self.animation.n_keyframes = 0
        else:
            self.animation.n_keyframes = 4
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager, data["anim"])

