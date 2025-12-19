from src.utils.definition import Monster, BattleMonster, Skill
class SkillExecutor:
    def __init__(self):
        self.handlers = {
            "attack": self.handle_attack,
            "heal": self.handle_heal,
            "apply_effect": self.handle_apply_effect,
            "apply_status": self.handle_apply_status,
            "special": self.handle_special
        }

        self.PHASE_ORDER = [
            "damage",
            "heal",
            "effect",
            "status",
            "special"
        ]
        self.DEFAULT_PHASE = {
            "attack": "damage",
            "heal": "heal",
            "apply_effect": "effect",
            "apply_status": "status",
            "special": "special"
        }
        self.EFFECT_NAME = {
            "attack_up": "Atteck UP",
            "attack_down": "Attack DOWN",
            "defense_up": "Defense UP",
            "defense_down": "Defense DOWN",
            "speed_up": "Speed UP",
            "speed_down": "Speed DOWN"
        }
        self.STATUS_NAME = {
            "bleed": "Bleed",
            "regen": "Regen",
            "on_fire": "On Fire",
            "thorn": "Thorn",
            "invincible": "Invincible",
            "vulnerable": "Vulnerable",
            "poison": "Poison",
            "stun": "Stun",
            "sleep": "Sleep",
            "lifesteal": "Lifesteal"
        }

    def apply_skill(self, user: BattleMonster, enemy: BattleMonster, s: Skill):
        skill = s.to_dcit()
        events = []
        
        effects_by_phase = {p: [] for p in self.PHASE_ORDER}


        for effect in skill.get("effects", []):
            phase = effect.get("phase") or self.DEFAULT_PHASE.get(effect["type"])
            if phase not in effects_by_phase:
                raise ValueError(f"Unknown phase: {phase}")
            effects_by_phase[phase].append(effect)
        
        for phase in self.PHASE_ORDER:
            for effect in effects_by_phase[phase]:
                handler = self.handlers.get(effect["type"])
                if not handler:
                    raise ValueError(f"Unknown effect type: {effect["type"]}")
                result = handler(user, enemy, effect)
                if result:
                    events.append(result)
            
        return events
    def apply_potion(self, user: BattleMonster, enemy: BattleMonster, potion_effects: list[dict]):
        events = []
        
        effects_by_phase = {p: [] for p in self.PHASE_ORDER}


        for effect in potion_effects:
            phase = effect.get("phase") or self.DEFAULT_PHASE.get(effect["type"])
            if phase not in effects_by_phase:
                raise ValueError(f"Unknown phase: {phase}")
            effects_by_phase[phase].append(effect)
        
        for phase in self.PHASE_ORDER:
            for effect in effects_by_phase[phase]:
                handler = self.handlers.get(effect["type"])
                if not handler:
                    raise ValueError(f"Unknown effect type: {effect["type"]}")
                result = handler(user, enemy, effect)
                if result:
                    events.append(result)
            
        return events
    def element_counter(self, element_1, element_2):
        """ 
        If element_1 counter element_2, return True, else False.
        """
        counter_table = {
            "grass": set(["water"]),
            "fire": set(["grass"]),
            "water": set(["fire"]),
            "dark": set(["grass", "fire", "water", "dark"]),
            "divine": set(["dark"]),
            "neutral": set()
        }
        if element_2 in counter_table[element_1]:
            return True
        else:
            return False
    @staticmethod
    def effect_identity(effect: dict) -> tuple:
        return(
            effect["type"],
            effect["id"],
            effect.get("method"),
            effect.get("value")
        )
    #--------------
    # Effects
    #--------------

    def handle_attack(self, user: BattleMonster, enemy: BattleMonster, effect: dict):
        from random import random
        chance = effect.get("chance", 1.0)
        if chance == 1.0:
            pass
        else:
            r = random()
            if r < chance:
                pass
            else:
                return {
                    "type": "failed_chance"
                }

        power = effect.get("power")
        base_dmg = user.temp_stats["attack"] * power
        target = enemy if effect["target"] == "enemy" else user
        if self.element_counter(effect["element"], target.element):
            base_dmg *= 1.50
        elif self.element_counter(target.element, effect["element"]):
            base_dmg *= 0.67
        final_dmg = round(base_dmg - target.temp_stats["defense"])

        accuracy = (user.temp_stats["speed"] - target.temp_stats["speed"] + 80) / 100
        chance = random()
        if chance < accuracy:
            return {
                "type": "damage",
                "target": target,
                "amount": final_dmg,
                "text": f"Dealt {final_dmg} to {target.base.name}"
            }
        else:
            return {
                "type": "missed",
                "text": f"{user.base.name} missed it's attack."
            }
    
    def handle_heal(self, user: BattleMonster, enemy: BattleMonster, effect: dict):
        chance = effect.get("chance", 1.0)
        if chance == 1.0:
            pass
        else:
            from random import random
            r = random()
            if r < chance:
                pass
            else:
                return {
                    "type": "failed_chance"
                }

        value = effect.get("value")
        target = enemy if effect["target"] == "enemy" else user
        method = effect.get("method")
        if method == "add":
            final_regen = round(value)
        elif method == "lost_hp":
            final_regen = round((target.max_hp - target.hp) * value)
        elif method == "max_hp":
            final_regen = round(target.max_hp * value)
        
        return {
            "type": "heal",
            "target": target,
            "amount": final_regen,
            "text": f"{target.base.name} healed {final_regen} hp."
        }
    
    def handle_apply_effect(self, user: BattleMonster, enemy: BattleMonster, effect: dict):
        from random import random
        chance = effect.get("chance", 1.0)
        if chance == 1.0:
            pass
        else:
            r = random()
            if r < chance:
                pass
            else:
                return {
                    "type": "failed_chance"
                }
        target = enemy if effect["target"] == "enemy" else user
        new_key = self.effect_identity(effect)

        for existing in target.effects:
            if self.effect_identity(existing) == new_key:
                existing["duration"] += effect["duration"]
                return {
                    "type": "extend_effect",
                    "target": target,
                    "id": effect["id"],
                    "added_duration": effect["duration"],
                    "total_duration": existing["duration"],
                    "text": f"{target.base.name}'s {self.EFFECT_NAME[effect["id"]]} extended for {effect["duration"]} rounds. (Total {existing["duration"]} rounds)"
                }
        target.pending_effects.append(effect.copy())
        return {
            "type": "apply_effect",
            "target": target,
            "id": effect["id"],
            "duration": effect["duration"],
            "text": f"{target.base.name} got {self.EFFECT_NAME[effect["id"]]} for {effect["duration"]} rounds."
        }
    
    def handle_apply_status(self, user: BattleMonster, enemy: BattleMonster, effect: dict):
        from random import random
        chance = effect.get("chance", 1.0)
        if chance == 1.0:
            pass
        else:
            r = random()
            if r < chance:
                pass
            else:
                return {
                    "type": "failed_chance"
                }
        target = enemy if effect["target"] == "enemy" else user
        for s in target.status:
            if s["id"] == effect["id"]:
                s["duration"] += effect["duration"]
                return {
                    "type": "extend_status",
                    "target": target,
                    "id": effect["id"],
                    "added_duration": effect["duration"],
                    "total_duration": s["duration"],
                    "text": f"{target.base.name}'s {self.STATUS_NAME[effect["id"]]} extended for {effect["duration"]} rounds. (Total {s["duration"]} rounds)"
                }
        target.pending_status.append(effect.copy())
        return {
            "type": "apply_status",
            "target": target,
            "id": effect["id"],
            "duration": effect["duration"],
            "text": f"{target.base.name} got {self.STATUS_NAME[effect["id"]]} for {effect["duration"]} rounds."
        }
    def handle_special(self, user: BattleMonster, enemy: BattleMonster, effect: dict):
        from random import random
        chance = effect.get("chance", 1.0)
        if chance == 1.0:
            pass
        else:
            r = random()
            if r < chance:
                pass
            else:
                return {
                    "type": "failed_chance"
                }
        if effect["id"] == "additional_energy":
            value = effect["value"]
            return {
                "type": "special",
                "id": "additional_energy",
                "value": value,
                "text": f"Gain additional {value} energy."
            }
        elif effect["id"] == "eliminate_dark":
            target = enemy if effect["target"] == "enemy" else user
            if target.element == "dark":
                target.take_damage(target.hp)
                return {
                    "type": "special",
                    "id": "eliminate_dark",
                    "text": f"The darkness was eliminated, {target.base.name} HP drop to 0."
                }
            return {
                "type": "special",
                "id": "eliminate_dark",
                "text": f"The darkness was eliminated."
            }
        elif effect["id"] == "purify":
            target = enemy if effect["target"] == "enemy" else user
            target.effects = [e for e in target.effects if e not in ("attack_down", "defense_down", "speed_down")]
            target.status = [s for s in target.status if s not in ("bleed", "on_fire", "vulnerable", "stun", "sleep", "poison")]
            return {
                "type": "special",
                "id": "purify",
                "target": target,
                "text": f"{target.base.name} was purified, removed all negative effects and status."
            }
        elif effect["id"] == "tunnel_escape":
            return {
                "type": "special",
                "id": "tunnel_escape",
                "user": user,
                "text": f"{user.base.name} used Tunnel Escape."
            }
                    