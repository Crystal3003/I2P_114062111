from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.utils.definition import Monster, Item

class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        return

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        anim_sprite_path: str,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
        monsters: list[Monster] | None = [],
        can_be_challenged_again: bool | None = False,
        rewards: list[Item] | None = []
    ) -> None:
        super().__init__(x, y, game_manager, anim_sprite_path)
        self.classification = classification
        self.max_tiles = max_tiles
        self.monsters = monsters
        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False

        self.can_be_challenged_again = can_be_challenged_again
        self.rewards = rewards


    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        self.animation.update_pos(self.position)

    def enter_battle_update(self, dt):
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            scene_manager.change_scene("battle", 
                                       game_manager=self.game_manager, 
                                       bg_path="backgrounds/background1.png", 
                                       battle_type='trainer',
                                       enemy_monsters = self.monsters,
                                       can_be_challenged_again = self.can_be_challenged_again,
                                       rewards = self.rewards)
    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

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
        '''
        TODO: Create hitbox to detect line of sight of the enemies towards the player
        '''
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
            return
        '''
        TODO: Implement line of sight detection
        If it's detected, set self.detected to True
        '''
        player_rect = player.rect
        if los_rect.colliderect(player_rect):
            self.detected = True
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        anim = data.get("anim")
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        can_ba_challenged_again = data.get("can_ba_challenged_again", False)
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        monsters = []
        for m in data.get("monsters"):
            monsters.append(Monster(**m))
        rewards = []
        for r in data.get("rewards", []):
            rewards.append(Item(**r))
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            anim,
            classification,
            max_tiles,
            facing,
            monsters,
            can_ba_challenged_again,
            rewards
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        base["can_ba_challenged_again"] = self.can_be_challenged_again
        monsters = []
        for m in self.monsters:
            monsters.append(m.to_dict())
        base["monsters"] = monsters
        rewards = []
        for r in self.rewards:
            rewards.append(r.to_dict())
        return base