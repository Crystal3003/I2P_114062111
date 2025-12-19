import pygame as pg 
from src.utils import GameSettings 
from src.sprites import BackgroundSprite 
from src.scenes.scene import Scene 
from src.interface.components import Button, TextedButton
from src.core.services import scene_manager, sound_manager, input_manager 
from src.core.managers import GameManager 
from typing import override 
from src.utils import GameSettings, Logger
from src.entities.pokemon import Pokemon 
from src.utils.definition import Monster, BattleMonster, Skill
from src.interface.description_manager import DescriptionManager
from src.utils.skill_executor import SkillExecutor
from src.data.bag import Bag
from src.data.battle_monster_menu import BattleMonsterMenu
from src.data.battle_item_menu import BattleItemMenu, Item
class BattleScene(Scene): 
    background: BackgroundSprite 
# options 
    attack_button: Button 
    run_button: Button 
    capture_button: Button
    page_btns: list[TextedButton]
    def __init__(self): 
        super().__init__()
        self.player_turn = True 
        self.battle_type = None
        self.battle_over = False
        self.bg_path = "backgrounds/background1.png"
        self.done_option = False 
        self.enemy_moved = False
        self.captured = False
        self.added_energy = False
        self.switch_reason = None
        self.round_started = False
        self.game_manager = GameManager.load("saves/game0.json")
        self.current_page = "main"
        self.skill_executor = SkillExecutor()
        self.event_queue = []
        # descriptions 
        self.dm = DescriptionManager("assets/fonts/Pokemon Solid.ttf", 16)
        self.dm.set_hint("assets/fonts/Minecraft.ttf") 
        self.your_turn = pg.font.Font("assets/fonts/Minecraft.ttf", 16).render("It's your turn now", 0, (255, 229, 0)) 
        self.enemy_turn = pg.font.Font("assets/fonts/Minecraft.ttf", 16).render("It's enemy's turn now", 0, (255, 229, 0)) 
        #player's monster
        self.player_monsters = []
        self.player_current_monster = None
        self.player_energy = 0
        #enemy and bush monster 
        self.opponent_monsters = []
        self.bush_monster = None
        self.opponent_current_monster =  None
        self.enemy_energy = 0
        self.emi = 0 # enemy move index
        #buttons 
        bx = GameSettings.SCREEN_WIDTH * 0.7
        dx = GameSettings.SCREEN_WIDTH * 0.1
        by = GameSettings.SCREEN_HEIGHT - 75
        self.act_button = TextedButton("Act", 18, bx/4*0 + dx, by, 6, lambda: self.change_page("act"))
        self.bag_button = TextedButton("Bag", 18, bx/4*1 + dx, by, 6, lambda: self.change_page("bag"))
        self.switch_button = TextedButton("Switch", 18, bx/4*2 + dx, by, 6, lambda: self.change_page("switch"))
        self.escape_button = TextedButton("Escape", 18, bx/4*3 + dx, by, 6, lambda: self.change_page("escape"))
        self.capture_button = TextedButton("Capture", 18, bx/4*0 + dx, by, 6, lambda: self.change_page("capture"))
        self.page_btns = []
        self.x_button = Button("UI/button_x.png", "UI/button_x_hover.png",
                               GameSettings.SCREEN_WIDTH / 2 + 315, GameSettings.SCREEN_HEIGHT / 2 - 265,
                               50, 50, lambda: self.change_page())
        self.bag = self.game_manager.bag
        self.monster_menu = BattleMonsterMenu(self.game_manager.bag._monsters_data, self.player_current_monster)
        self.item_menu = BattleItemMenu(self.game_manager.bag._items_data)
    def set_params(self, game_manager: GameManager, battle_type=None, bg_path="backgrounds/background1.png", enemy_monsters: list[Monster] | None = []): 
        self.bg_path = bg_path
        self.battle_type = battle_type 
        self.game_manager = game_manager
        self.player_monsters = [m for m in self.game_manager.bag._monsters_data]
        if battle_type == "trainer":
            self.opponent_monsters = enemy_monsters
            self.opponent_current_monster = BattleMonster(self.opponent_monsters[0])
        elif battle_type == "bush":
            self.bush_monster = self.generate_bush_monster()
            self.opponent_monsters = [self.bush_monster]
            self.opponent_current_monster = BattleMonster(self.opponent_monsters[0])
    def change_page(self, page: str | None = "main"):
        """change_page() -> change to main page"""
        self.monster_menu.close()
        self.item_menu.close()
        self.current_page = page
        self.generate_buttons(page)
        if page == "switch":
            self.monster_menu.current_monster = self.player_current_monster
            self.monster_menu.menu.items = self.player_monsters
            self.monster_menu.open()
        elif page == "bag":
            self.item_menu.menu.items = self.game_manager.bag._items_data
            self.item_menu.open()
        Logger.debug(f"Changed page to {page}")

    def generate_bush_monster(self):
        import random, json
        bag = self.game_manager.bag
        average_lvl = 0
        for m in bag._monsters_data:
            average_lvl += m.level
        average_lvl = max(1, average_lvl // len(bag._monsters_data))
        lvl = max(1, average_lvl + random.randint(-5,5))
        with open("monster_info/monsters/all_monsters_id.json", "r", encoding="utf-8") as f:
            all_monster_id = json.load(f)
        stage_1_ids = all_monster_id.get("stage_1")
        monster_id = random.choice(stage_1_ids)
        bush_monster = Monster.from_id(monster_id)
        bush_monster.grow_to_level(lvl)
        return bush_monster
    
    def capture(self):
        self.dm.add("You captured a new pokemon!")
        self.done_option = True 
        self.captured = True
        self.battle_over = True

    @override 
    def enter(self) -> None:
        self.player_turn = True 
        self.battle_over = False
        self.done_option = False 
        self.enemy_moved = False
        self.captured = False 
        self.player_current_monster = None
        self.player_energy = 0
        self.enemy_energy = 0
        self.change_page("switch")
        self.switch_reason = "initialize"
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg") 
        self.background = BackgroundSprite(self.bg_path) 
        if self.battle_type == 'bush': 
            self.dm.set([f"Wild {self.opponent_current_monster.base.name} Appeared!",
                         f"Choose your monster"])
        elif self.battle_type == 'trainer':
            self.dm.set([f"Enemy sent {self.opponent_current_monster.base.name}",
                         f"choose your monster"])
    @override 
    def exit(self) -> None: 
        for m in self.game_manager.bag._monsters_data:
            m.update_level()
        pass 
    @override 
    def update(self, dt: float) -> None:
        if self.dm.descriptions:
            self.dm.update(dt)
        elif self.player_turn: 
            if self.current_page == "main":
                self.bag_button.update(dt)
                self.switch_button.update(dt)
                self.escape_button.update(dt)
                if self.battle_type == 'bush' and self.bush_monster.hp == 0:
                    self.capture_button.update(dt)
                else:
                    self.act_button.update(dt)
            else:
                for b in self.page_btns:
                    b.update(dt)
            if self.current_page == "act":
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.change_page()
            elif self.current_page == "switch":
                if not self.monster_menu.active:
                    self.change_page()
                    return
                if self.switch_reason == "initialize" or self.switch_reason == "tunnel_escape" or self.switch_reason == "last_no_hp":
                    self.monster_menu.locked = True
                self.monster_menu.update(dt)
                switched_monster_index = self.monster_menu.poll_monster_index()
                if switched_monster_index is not None:
                    self.player_current_monster = BattleMonster(self.player_monsters[switched_monster_index])
                    self.dm.add(f"Go! {self.player_current_monster.base.name}!")
                    if not(self.switch_reason == "initialize" or self.switch_reason == "tunnel_escape" or self.switch_reason == "last_no_hp"):
                        self.player_energy -= 3 
                    self.change_page()
                    self.event_queue.append({"type":"switch"})
            elif self.current_page == "bag":
                if not self.item_menu.active:
                    self.change_page()
                    return
                self.item_menu.update(dt)
                used_item_id = self.item_menu.poll_item_id()
                if used_item_id is not None:
                    item = Item.from_id(used_item_id)
                    self.player_energy -= 3
                    for i in self.game_manager.bag._items_data:
                        if i.id == item.id:
                            i.count -= 1
                            if i.count <= 0:
                                self.game_manager.bag._items_data.remove(i)
                            break
                            
                    self.change_page()
                    self.dm.add(f"You used {item.name}")
                    events = self.skill_executor.apply_potion(self.player_current_monster, self.opponent_current_monster, item.effects)
                    self.event_queue.extend(events)

        if self.player_current_monster:
            self.player_current_monster.update(dt)
        self.opponent_current_monster.update(dt)
    def generate_buttons(self, page: str):
        self.page_btns.clear()
        sw = GameSettings.SCREEN_WIDTH
        w = GameSettings.SCREEN_WIDTH * 0.7
        dx = GameSettings.SCREEN_WIDTH * 0.15
        h = GameSettings.SCREEN_HEIGHT - 75
        btn_w = TextedButton("", 18, 0, 0, 6).hitbox.width
        space = 225
        if page == "act":
            skill_set = self.player_current_monster.skill_set
            n = len(skill_set)
            start_x = (sw - n*btn_w - (n-1)*(btn_w-space)) / 2
            for i, skill in enumerate(skill_set):
                btn = TextedButton(skill.name, 18, start_x + i*space - dx , h, 6, lambda s = skill: self.button_function("act", s))
                self.page_btns.append(btn)
            return
        elif page == "bag":
            pass
        elif page == "switch":
            pass
        elif page == "escape":
            run_btn = TextedButton("Run", 18, w/2, h, 6, lambda e = True: self.button_function("escape", e))
            stay_btn = TextedButton("Stay", 18, w, h, 6, lambda e = False: self.button_function("escape", e))
            self.page_btns.extend([run_btn, stay_btn])
        elif page == "capture":
            pass
    def button_function(self, move, descision):
        if move == "act":
            descision: Skill
            if self.player_energy < descision.ec:
                self.dm.add(f"You don't have enough energy")
                return
            self.player_energy -= descision.ec
            self.player_current_monster.base.exp_from_energy(descision.ec)
            self.dm.add(f"You used {descision.name}")
            events = self.skill_executor.apply_skill(self.player_current_monster, self.opponent_current_monster, descision)
            self.event_queue.extend(events)
        elif move == "bag":
            pass
        elif move == "switch":
            pass
        elif move == "escape":
            descision: bool
            if descision:
                self.dm.add("You ran away from the battle")
                self.battle_over = True
            else:
                self.change_page()

    @override 
    def draw(self, screen: pg.Surface) -> None: 
        self.background.draw(screen) 
        self.dm.draw(screen)
    #sprits 
        if self.player_current_monster:
            screen.blit(self.player_current_monster.base.battle_img_player_side, (350, GameSettings.SCREEN_HEIGHT - 100 
                                                                                - self.player_current_monster.base.battle_img_player_side.get_height())) 
            self.player_current_monster.show_info(screen, 650, 530) 
        screen.blit(self.opponent_current_monster.base.battle_img_enemy_side, (700, 170))
        self.opponent_current_monster.show_info(screen, 50, 200, True)
        pe_text = pg.font.Font("assets/fonts/minecraft.ttf", 24).render(f"{self.player_energy}/15",0,(0, 0, 0))
        ee_text = pg.font.Font("assets/fonts/minecraft.ttf", 24).render(f"{self.enemy_energy}/15",0,(0, 0, 0))
        screen.blit(pe_text, (150, 550))
        screen.blit(ee_text, (1000, 250))
        # in battle 
        if self.dm.descriptions: 
            pass
        
        elif self.current_page == "switch":

            self.monster_menu.draw(screen)
        elif self.current_page == "bag":

            self.item_menu.draw(screen)

        #-----------------
        # deal with events
        #-----------------
        elif self.event_queue:
            event = self.event_queue.pop(0)
            while self.event_queue and event["type"] == "failed_chance":
                event = self.event_queue.pop(0)
            if event["type"] == "failed_chance":
                pass
            
            # In Phase Order
            elif event["type"] == "damage":
                target: BattleMonster
                target = event["target"]
                amount = event["amount"]
                actual = target.take_damage(amount)
                if target == self.player_current_monster:
                    event["text"] = f"Dealt {actual} to your {target.base.name}."
                else:
                    event["text"] = f"Dealt {actual} to the opponent's {target.base.name}."
            elif event["type"] == "heal":
                target: BattleMonster
                target = event["target"]
                amount = event["amount"]
                actual = target.heal(amount)
                if target == self.player_current_monster:
                    event["text"] = f"Your {target.base.name} healed {actual} hp."
                else:
                    event["text"] = f"The opponent's{target.base.name} healed {actual} hp."
            elif event["type"] == "extend_effect":
                pass # Finished in SkillExecutor
            elif event["type"] == "apply_effect":
                pass # Finished in SkillExecutor
            elif event["type"] == "extend_status":
                pass # Finished in SkillExecutor
            elif event["type"] == "apply_status":
                pass # Finished in SkillExecutor
            elif event["type"] == "special":
                if event["id"] == "additional_energy":
                    value = event["value"]
                    if self.player_turn: # Player just finished move, so added energy on player.
                        self.player_energy = min(self.player_energy + value, 15)
                    else:
                        self.enemy_energy = min(self.enemy_energy + value, 15) 
                elif event["id"] == "tunnel_escape":
                    self.player_current_monster = None
                    self.switch_reason = "tunnel_escape"
                    self.player_turn = True
                    self.change_page("switch")
            text = event.get("text", None)
            if text:
                self.dm.add(text)

            # All the events are executed
            if self.event_queue == []:
                # reduce all effects duration
                for effect in self.player_current_monster.effects:
                    effect["duration"] -= 1
                for i in range(len(self.player_current_monster.effects)-1, -1, -1):
                    if self.player_current_monster.effects[i]["duration"] <= 0:
                        self.player_current_monster.effects.pop(i)
                self.player_current_monster.update_and_tick_effects()
                self.player_current_monster.update_status()

                for effect in self.opponent_current_monster.effects:
                    effect["duration"] -= 1
                for i in range(len(self.opponent_current_monster.effects)-1, -1, -1):
                    if self.opponent_current_monster.effects[i]["duration"] <= 0:
                        self.opponent_current_monster.effects.pop(i)
                self.opponent_current_monster.update_and_tick_effects()
                self.opponent_current_monster.update_status()

                # switch turn
                if self.switch_reason == "tunnel_escape" or self.switch_reason == "initialize" or self.switch_reason == "last_no_hp":
                    self.player_turn = True
                else:
                    self.player_turn = False
                if self.switch_reason == "tunnel_escape":
                    self.added_energy = True
                else:
                    self.added_energy = False
                self.change_page()
                self.switch_reason = None
                self.round_started = False
        
        elif self.player_turn and not self.battle_over:
            # This is start of player's turn.
            # Tick status
            if not self.round_started:
                self.player_current_monster.tick_status()
                self.opponent_current_monster.tick_status()
                self.round_started = True
            # check if need to switch or already lost
            if self.player_current_monster.hp <= 0:
                for m in self.player_monsters:
                    if m.hp > 0:
                        self.battle_over = False
                        self.switch_reason = "last_no_hp"
                        self.change_page("switch")
                        return
                self.dm.add("All your monsters are beaten!")
                self.dm.add("You lost the battle!")
                self.battle_over = True
                return
            screen.blit(self.your_turn, (GameSettings.SCREEN_WIDTH - 150, GameSettings.SCREEN_HEIGHT - 20)) 
            # Gain energy
            if not self.added_energy:
                self.player_energy = min(self.player_energy + 3, 15)
                self.added_energy = True
            # Selecting action
            elif self.player_turn: 
                if self.current_page == "main":
                    self.bag_button.draw(screen)
                    self.switch_button.draw(screen)
                    self.escape_button.draw(screen)
                    if self.battle_type == 'bush' and self.bush_monster.hp == 0:
                        self.capture_button.draw(screen)
                    else:
                        self.act_button.draw(screen)
                else:
                    for b in self.page_btns:
                        b.draw(screen)
       
        elif not self.player_turn and not self.battle_over: 
            # This is start of enemy's turn
            # Tick status
            if not self.round_started:
                self.player_current_monster.tick_status()
                self.opponent_current_monster.tick_status()
                self.round_started = True
            # check if need to switch or already lost
            if self.opponent_current_monster.hp <= 0:
                for m in self.opponent_monsters:
                    if m.hp > 0:
                        self.opponent_current_monster = BattleMonster(m)
                        self.battle_over = False
                        return
                self.dm.add("All defeated the opponent!")
                self.dm.add("You won the battle!")
                self.battle_over = True
                return
            # Gain energy
            if not self.added_energy and self.emi == 0:
                self.enemy_energy = min(self.enemy_energy + 3, 15)
                self.added_energy = True
            #enemy's turn 
            elif not self.enemy_moved:
                if self.emi == 0:
                    self.dm.add("The opponent is about to attack")
                elif self.emi == 1:
                    opponent_skill_set = self.opponent_current_monster.skill_set
                    import random
                    skill = random.choice(opponent_skill_set)
                    if self.enemy_energy < skill.ec:
                        return
                    self.enemy_energy -= skill.ec
                    events = self.skill_executor.apply_skill(self.opponent_current_monster, self.player_current_monster, skill)
                    self.event_queue.extend(events)
                    self.dm.add(f"The opponent used {skill.name}")
                    self.enemy_moved = True
                self.emi += 1
            else:
                self.emi = 0
                self.player_turn = True 
                self.enemy_moved = False
                self.added_energy = False 
                self.round_started = False
        else:
            #battle is over
            if self.captured:
                self.game_manager.bag._monsters_data.append(self.bush_monster)
            scene_manager.change_scene("game")