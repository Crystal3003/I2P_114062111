from __future__ import annotations
from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.entities.shop.shop import Shop
    from src.data.bag import Bag
    from src.maps.navigate_point import NavigatePoint
class GameManager:
    # Entities
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    shops: dict[str, list[Shop]]
    bag: "Bag"
    navigate_points: dict[str, list[NavigatePoint]]
    # Map properties
    current_map_key: str
    maps: dict[str, Map]
    # Changing Scene properties
    should_change_scene: bool
    next_map: str
    next_map_pos: Position
    
    def __init__(self, maps: dict[str, Map], start_map: str, 
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]],
                 shops: dict[str, list[Shop]],
                 navigate_points: dict[str, list[NavigatePoint]],
                 bag: Bag | None = None):
                     
        from src.data.bag import Bag
        # Game Properties
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        self.enemy_trainers = enemy_trainers
        self.shops = shops
        self.navigate_points = navigate_points
        self.bag = bag if bag is not None else Bag([], [])
        # Check If you should change scene
        self.should_change_scene = False
        self.next_map = ""
        self.next_map_pos = None
        
    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers[self.current_map_key]
    @property
    def current_shops(self) -> list[Shop]:
        return self.shops[self.current_map_key]
    @property
    def current_navigate_points(self) -> list[NavigatePoint]:
        return self.navigate_points[self.current_map_key]
    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters
    
    def switch_map(self, target: str, dest_pos: Position) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return
        
        self.next_map = target
        self.should_change_scene = True
        if dest_pos:
            self.next_map_pos = dest_pos
        else:
            self.next_map_pos = self.maps[self.next_map].spawn
    def try_switch_map(self) -> bool:
        if self.should_change_scene:
            self.current_map_key = self.next_map
            self.next_map = ""
            self.should_change_scene = False
            if self.player:
                self.player.position = self.next_map_pos.copy()
                self.player.animation.update_pos(self.player.position)
            return True
    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers[self.current_map_key]:
            if rect.colliderect(entity.animation.rect):
                return True
        for shop in self.shops[self.current_map_key]:
            if rect.colliderect(shop.animation.rect):
                return True
        return False
        
    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")
             
    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}, ignoring load function")
            return None

        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, object]:
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            block = m.to_dict()
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            block["shops"] = [s.to_dict() for s in self.shops.get(key, [])]
            block["navigate_points"] = [n.to_dict() for n in self.navigate_points.get(key, [])]
            map_blocks.append(block)
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": self.player.to_dict() if self.player is not None else None,
            "bag": self.bag.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.entities.shop.shop import Shop
        from src.maps.navigate_point import NavigatePoint
        from src.data.bag import Bag
        
        Logger.info("Loading maps")
        maps_data = data["map"]
        maps: dict[str, Map] = {}
        player_spawns: dict[str, Position] = {}
        trainers: dict[str, list[EnemyTrainer]] = {}
        shops: dict[str, list[Shop]] = {}
        navigate_points: dict[str, list[NavigatePoint]] = {}
        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)
            sp = entry.get("player")
            if sp:
                player_spawns[path] = Position(
                    sp["x"] * GameSettings.TILE_SIZE,
                    sp["y"] * GameSettings.TILE_SIZE
                )
        current_map = data["current_map"]
        gm = cls(
            maps, current_map,
            None, # Player
            trainers,
            shops,
            navigate_points,
            bag=None
        )
        gm.current_map_key = current_map
        
        Logger.info("Loading enemy trainers")
        for m in data["map"]:
            raw_data = m["enemy_trainers"]
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]

        Logger.info("Loading shops")
        for m in data["map"]:
            raw_data = m["shops"]
            gm.shops[m["path"]] = [Shop.from_dict(s, gm) for s in raw_data]

        Logger.info("Loading navigate points")
        for m in data["map"]:
            raw_data = m["navigate_points"]
            gm.navigate_points[m["path"]] = [NavigatePoint.from_dict(n) for n in raw_data]

        Logger.info("Loading Player")
        if data.get("player"):
            gm.player = Player.from_dict(data["player"], gm)
        
        Logger.info("Loading bag")
        from src.data.bag import Bag as _Bag
        gm.bag = Bag.from_dict(data.get("bag", {})) if data.get("bag") else _Bag([], [])

        return gm