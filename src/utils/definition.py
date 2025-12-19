from pygame import Rect
import pygame as pg
from .settings import GameSettings
from dataclasses import dataclass
from enum import Enum
from typing import overload, TypedDict, Protocol, override
import json
import os
from .logger import Logger
MouseBtn = int
Key = int

Direction = Enum('Direction', ['UP', 'DOWN', 'LEFT', 'RIGHT', 'NONE'])

@dataclass
class Position:
    x: float
    y: float
    
    def copy(self):
        return Position(self.x, self.y)
        
    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
@dataclass
class PositionCamera:
    x: int
    y: int
    
    def copy(self):
        return PositionCamera(self.x, self.y)
        
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
        
    def transform_position(self, position: Position) -> tuple[int, int]:
        return (int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_position_as_position(self, position: Position) -> Position:
        return Position(int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_rect(self, rect: Rect) -> Rect:
        return Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

@dataclass
class Teleport:
    pos: Position
    destination: str
    dest_pos: Position
    @overload
    def __init__(self, x: int, y: int, destination: str, dest_x:int, dest_y:int) -> None: ...
    @overload
    def __init__(self, pos: Position, destination: str, dest_pos: Position) -> None: ...

    def __init__(self, *args, **kwargs):
        if isinstance(args[0], Position):
            self.pos = args[0]
            self.destination = args[1]
            self.dest_pos = args[2]
        else:
            x, y, dest, dest_x, dest_y = args
            self.pos = Position(x, y)
            self.destination = dest
            self.dest_pos = Position(dest_x, dest_y)
    
    def to_dict(self):
        return {
            "x": self.pos.x / GameSettings.TILE_SIZE,
            "y": self.pos.y / GameSettings.TILE_SIZE,
            "destination": self.destination,
            "dest_x": self.dest_pos.x / GameSettings.TILE_SIZE,
            "dest_y": self.dest_pos.y / GameSettings.TILE_SIZE
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, 
                   data["destination"], 
                   data["dest_x"] * GameSettings.TILE_SIZE, data["dest_y"]* GameSettings.TILE_SIZE)
    
class Skill:
    def __init__(self, id):
        self.id = id
        path = f"monster_info/moves/{id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.name = data.get("name")
        self.ec = data.get("ec")
        self.effects = data.get("effects") 
    def to_dcit(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ec": self.ec,
            "effects": self.effects
        }

class Monster:
    def __init__(self, *,
                 id, hp, max_hp, defense, attack, level, exp: int | None = 0, skill_set: list[str] | None = None):
        from src.sprites import Sprite
        path = f"monster_info/monsters/{id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.id = id
        self.name = data.get("name")
        self.element = data.get("element")
        self.speed = data.get("base_stats").get("speed")
        # Sprites
        menu_sprite_path = data.get("sprite", "ingame_ui/options1.png") 
        self.info_img = Sprite(menu_sprite_path, (50, 50))
        
        battle_sprite_path = data.get("battle_sprite")
        battle_img = Sprite(battle_sprite_path)
        sheet_w = battle_img.image.get_width()
        sheet_h = battle_img.image.get_height()
        size = (sheet_h + 100, sheet_h + 100)
        frame_w = sheet_w // 2
        enemy_side = battle_img.image.subsurface(pg.Rect(0, 0, frame_w, sheet_h))
        player_side = battle_img.image.subsurface(pg.Rect(frame_w, 0, frame_w, sheet_h))
        self.battle_img_player_side = pg.transform.smoothscale(player_side, size)
        self.battle_img_enemy_side = pg.transform.smoothscale(enemy_side, size)

        self.hp = hp
        self.max_hp = max_hp
        self.defense = defense
        self.attack = attack
        self.level = level

        #exp
        self.exp = exp
        self.pending_exp = 0
        self.level_up_exp = self.exp_to_next_level(self.level)
        if skill_set is not None and skill_set != []:
            self.skill_set = [Skill(skill) for skill in skill_set]
        else:
            self.skill_set = [Skill(self.data.get("moves", {}).get("default"))]
        
    def show_info(self, screen: pg.Surface, x, y, is_enemy: bool | None = False):
        from src.sprites import Sprite
        if is_enemy:
            frame = Sprite("UI/custom/UI_Flat_Banner05a.png", (480, 70))
        else:
            frame = Sprite("UI/raw/UI_Flat_Banner04a.png", (480, 70))
        Name = pg.font.Font("assets/fonts/Minecraft.ttf", 14).render(f"{self.id}   Lv.{str(self.level)}", 0, (0, 0, 0))
        hp_ratio = self.hp / self.max_hp
        screen.blit(frame.image, (x, y))
        if is_enemy:
            screen.blit(self.info_img.image,  (x + 400, y + 10))
            Name_rect = Name.get_rect()
            screen.blit(Name, (x + 385 - Name_rect.width, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{self.hp} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 185, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 185 + 201 * (1 - hp_ratio), y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 95, y + 45))
        else:
            screen.blit(self.info_img.image,  (x + 30, y + 10))
            screen.blit(Name, (x + 95, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{self.hp} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 95, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 95, y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 305, y + 45))
    
    def grow_to_level(self, level):
        """Grow and evolution to certain level"""
        level = min(level, 99)
        upgrade_levels = level - self.level
        if upgrade_levels <= 0:
            return
        for _ in range(upgrade_levels):

            self.level_up()

            self.try_evolution()
        
    def update_level(self):
        self.level_up_exp = self.exp_to_next_level(self.level)
        self.exp += self.pending_exp
        self.pending_exp = 0
        while self.exp >= self.level_up_exp:
            self.exp -= self.level_up_exp
            self.level_up()
            self.try_evolution()
            self.level_up_exp = self.exp_to_next_level(self.level)


    def level_up(self):
        import random
        self.level += 1
        delta_hp = 7 + random.randint(-3, 3)
        self.hp += delta_hp
        self.max_hp += delta_hp 
        delta_attack = 4 + random.randint(-2, 2)
        self.attack += delta_attack
        delta_defense = 2 + random.randint(-1,1)
        self.defense += delta_defense
        path = f"monster_info/monsters/{self.id}.json"
        Logger.info(f"{self.name} level up! {self.level - 1}->{self.level}\
                    \nATK: {self.attack - delta_attack} -> {self.attack}\
                    \nDEF: {self.defense - delta_defense} -> {self.defense}\
                    \nHP: {self.max_hp - delta_hp} -> {self.max_hp}")
        with open(path,"r",encoding="utf-8") as f:
            data = json.load(f)
        for skill in data["moves"].get("learnset"):
            if self.level >= skill["level"] and skill["move"] not in [s.id for s in self.skill_set]:
                self.skill_set.append(Skill(skill["move"]))
                Logger.info(f"{self.name} learnet {Skill(skill["move"]).name}")

    def try_evolution(self):
        path = f"monster_info/monsters/{self.id}.json"
        with open(path,"r",encoding="utf-8") as f:
            data = json.load(f)
        evo = data.get("evolution", None)
        if not evo:
            pass
        elif self.level >= evo["value"]:
            next_id = evo["next"]
            path = f"monster_info/monsters/{next_id}.json"
            with open(path,"r",encoding="utf-8") as f:
                evo_data = json.load(f)
            Logger.info(f"{self.name} grown into {evo_data["name"]}!")
            self._load_from_json(evo_data)


    def _load_from_json(self, data: dict):
        from src.sprites import Sprite
        self.id = data["id"]
        self.name = data.get("name")
        self.element = data.get("element")

        base = data["base_stats"]
        self.hp = max(self.max_hp, base["hp"])
        self.max_hp = max(self.max_hp, base["hp"])
        self.attack = max(self.attack, base["attack"])
        self.defense = max(self.defense, base["defense"])
        self.speed = base["speed"]
        # Sprites
        menu_sprite_path = data.get("sprite", "ingame_ui/options1.png") 
        self.info_img = Sprite(menu_sprite_path, (50, 50))
        
        battle_sprite_path = data.get("battle_sprite")
        battle_img = Sprite(battle_sprite_path)
        sheet_w = battle_img.image.get_width()
        sheet_h = battle_img.image.get_height()
        size = (sheet_h + 100, sheet_h + 100)
        frame_w = sheet_w // 2
        enemy_side = battle_img.image.subsurface(pg.Rect(0, 0, frame_w, sheet_h))
        player_side = battle_img.image.subsurface(pg.Rect(frame_w, 0, frame_w, sheet_h))
        self.battle_img_player_side = pg.transform.smoothscale(player_side, size)
        self.battle_img_enemy_side = pg.transform.smoothscale(enemy_side, size)

        # skills
        self.skill_set = [Skill(s) for s in data["moves"]["default"]]
        self.level = data["moves"]["learnset"][0].get("level") or 1

        
    @classmethod
    def from_id(cls, id: str):
        path = f"monster_info/monsters/{id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = data["base_stats"]
        moves = data["moves"]
        return cls(
            id=data["id"],
            hp=base["hp"],
            max_hp=base["hp"],
            attack=base["attack"],
            defense=base["defense"],
            exp=0,
            level=1,
            skill_set=moves["default"]
        )
    def to_dict(self):
        return {
            "id": self.id,
            "hp":self.hp,
            "max_hp":self.max_hp,
            "defense":self.defense,
            "attack":self.attack,
            "level":self.level,
            "exp": self.exp,
            "skill_set": [skill.id for skill in self.skill_set]
        }
    def exp_to_next_level(self, level):
        if level <= 30:
            return 30 + level * 20
        elif self.level <= 70:
           return 650 + (level - 30) * 30
        else:
            return min(2500, 1850 + (level - 70) * 40)
    @override
    def update(self, dt):
        pass
    def exp_from_energy(self, ec: int):
        self.pending_exp += 4 + int(ec ** 1.3)
    @override
    def draw(self, screen):
        pass

class BattleMonster:
    def __init__(self, monster: Monster):
        self.base = monster
        self.hp = monster.hp
        self.display_hp = monster.hp
        self.max_hp = monster.max_hp
        self.element = monster.element 
        self.skill_set = monster.skill_set
        self.temp_stats = {
            "attack": monster.attack,
            "defense": monster.defense,
            "speed": monster.speed
        }
        self.stunned = False
        self.sleep = False
        self.pending_effects = []
        self.pending_status = []
        self.effects = []
        self.status = []
    def update(self, dt: float):
        speed = self.max_hp * 0.2 * dt
        if self.display_hp < self.hp:
            self.display_hp = min(self.display_hp + speed, self.hp)
        elif self.display_hp > self.hp:
            self.display_hp = max(self.display_hp - speed, self.hp)
        self.base.hp = self.hp

    def take_damage(self, amount) -> int:
        if amount <= 0:
            return 0
        actual = min(amount, self.hp)
        self.hp -= actual
        return actual
    
    def heal(self, amount) -> int:
        if amount <= 0:
            return 0
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual
        return actual
    def show_info(self, screen: pg.Surface, x, y, is_enemy: bool | None = False):
        from src.sprites import Sprite
        if is_enemy:
            frame = Sprite("UI/custom/UI_Flat_Banner05a.png", (480, 70))
        else:
            frame = Sprite("UI/raw/UI_Flat_Banner04a.png", (480, 70))
        Name = pg.font.Font("assets/fonts/Minecraft.ttf", 14).render(f"{self.base.id}   Lv.{str(self.base.level)}", 0, (0, 0, 0))
        hp_ratio = self.display_hp / self.max_hp
        screen.blit(frame.image, (x, y))
        if is_enemy:
            screen.blit(self.base.info_img.image,  (x + 400, y + 10))
            Name_rect = Name.get_rect()
            screen.blit(Name, (x + 385 - Name_rect.width, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{int(self.display_hp)} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 185, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 185 + 201 * (1 - hp_ratio), y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 95, y + 45))
        else:
            screen.blit(self.base.info_img.image,  (x + 30, y + 10))
            screen.blit(Name, (x + 95, y + 20))
            hp_text = pg.font.Font("assets/fonts/minecraft.ttf", 16).render(f"{int(self.display_hp)} / {self.max_hp}", 0, (0, 0, 0))
            pg.draw.rect(screen, (255, 0, 0), (x + 95, y + 50, 200, 5))
            pg.draw.rect(screen, (0, 255, 0), (x + 95, y + 50, 200 * hp_ratio, 5))
            screen.blit(hp_text, (x + 305, y + 45))
    def update_and_tick_effects(self):
        self.effects.extend(self.pending_effects)
        self.pending_effects.clear()
        self.temp_stats = {
            "attack": self.base.attack,
            "defense": self.base.defense,
            "speed": self.base.speed
        }
        for effect in self.effects:
            method = effect["method"]
            value = effect["value"]
            if effect["id"] == "attack_up":
                if method == "add":
                    self.temp_stats["attack"] += value
                elif method == "multiply":
                    self.temp_stats["attack"] *= value
            elif effect["id"] == "attack_down":
                if method == "add":
                    self.temp_stats["attack"] -= value
                elif method == "multiply":
                    self.temp_stats["attack"] *= value
            elif effect["id"] == "defense_up":
                if method == "add":
                    self.temp_stats["defense"] += value
                elif method == "multiply":
                    self.temp_stats["defense"] *= value
            elif effect["id"] == "defense_down":
                if method == "add":
                    self.temp_stats["defense"] -= value
                elif method == "multiply":
                    self.temp_stats["defense"] *= value
            elif effect["id"] == "speed_up":
                if method == "add":
                    self.temp_stats["speed"] += value
                elif method == "multiply":
                    self.temp_stats["speed"] *= value
            elif effect["id"] == "speed_down":
                if method == "add":
                    self.temp_stats["speed"] -= value
                elif method == "multiply":
                    self.temp_stats["speed"] *= value
    def update_status(self):
        self.status.extend(self.pending_status)
        self.pending_status.clear()
    def tick_status(self):
        self.stunned = False
        self.sleep = False
        for status in self.status:
            if status["id"] == "bleed":
                self.hp = max(self.hp - 50, 0)
            elif status["id"] == "regen":
                self.hp = min(self.hp + round(self.max_hp * 0.15), self.max_hp)
            elif status["id"] == "on_fire":
                self.hp = max(self.hp - round(self.hp * 0.2), 0)
            elif status["id"] == "thorn":
                pass # Effective when attacked
            elif status["id"] == "invincible":
                pass # Effective when attacked
            elif status["id"] == "vulnerable":
                pass # Effective when attacked
            elif status["id"] == "poison":
                self.hp = max(self.hp - round(self.max_hp * 0.15), 0)
            elif status["id"] == "stun":
                self.stunned = True
            elif status["id"] == "sleep":
                self.sleep = True
            status["duration"] -= 1
        for i in range(len(self.status) - 1, -1, -1):
            if self.status[i]["duration"] <= 0:
                self.status.pop(i)
class Item:
    def __init__(self, *, id: str, count: int | None = 1):
        from src.sprites import Sprite
        path = f"item_info/items/{id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.id = id
        self.name = data["name"]
        self.sprite_path = data["sprite_path"]
        self.img = Sprite(self.sprite_path, (30, 30))
        self.tags = data.get("tags", [])
        self.usable = data.get("usable", False)
        self.effects = data.get("effects", [])
        self.texts = data.get("texts", [])
        self.count = count
    @classmethod
    def from_dict(cls):
        pass
    @classmethod
    def from_id(cls, id):
        path = f"item_info/items/{id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            id=id,
            count=1
        )
    def to_dict(self):
        return {
            "id": self.id,
            "count": self.count 
        }
