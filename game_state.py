import json
import os
import time

MILESTONES = [
    (100, "Your first pull request!"),
    (1_000, "Promoted to Junior Dev"),
    (10_000, "Your code is now in production"),
    (100_000, "You've created a new JavaScript framework"),
    (1_000_000, "You ARE the vibe"),
    (10_000_000, "The simulation runs on your code"),
]

SAVE_FILE = "save.json"
SAVE_INTERVAL = 30.0

TOTAL_WAVES = 10


class GameState:
    def __init__(self):
        # Economy
        self.loc = 0.0
        self.total_loc = 0.0
        self.lifetime_loc = 0.0

        # Milestones
        self.milestones_reached = []
        self.pending_milestones = []

        # Combo
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_max_gap = 0.8

        # HP
        self.max_hp = 100
        self.hp = 100
        self.display_hp = 100.0
        self.ghost_hp = 100.0

        # Wave
        self.wave = 1
        self.waves_completed = 0

        # Perks (current run)
        self.perks = []  # list of perk dicts
        self.temp_buffs = []  # temporary buffs for next wave

        # Relics (permanent across runs)
        self.relics = []  # list of relic ids

        # Meta
        self.runs_completed = 0
        self.best_wave = 0
        self.total_enemies_killed = 0

        # Disable input timer (ransomware)
        self.input_disabled_timer = 0.0

        # Auto-attack from perks
        self.auto_attack_timer = 0.0

        # HP regen
        self.regen_timer = 0.0

        # Used revive this run
        self.used_revive = False

        self.last_save_time = time.time()

    def add_loc(self, amount):
        loc_mult = self._get_perk_value('loc_mult', 1.0)
        amount *= loc_mult
        self.loc += amount
        self.total_loc += amount
        self.lifetime_loc += amount
        self._check_milestones()

    def spend_loc(self, amount):
        if self.loc >= amount:
            self.loc -= amount
            return True
        return False

    def register_correct_key(self):
        self.combo += 1
        gap = self.combo_max_gap + self._get_perk_value('combo_window_bonus', 0)
        self.combo_timer = gap

    def register_wrong_key(self):
        self.combo = 0
        self.combo_timer = 0.0

    def get_combo_multiplier(self):
        if self.combo < 5:
            return 1.0
        elif self.combo < 15:
            return 1.5
        elif self.combo < 30:
            return 2.0
        elif self.combo < 50:
            return 3.0
        else:
            return 5.0

    def is_epic_mode(self):
        return self.combo >= 50

    def get_damage(self, base_damage=1):
        import random
        damage = base_damage

        # Flat bonus from perks
        damage += self._get_perk_value('flat_damage_bonus', 0)

        # Damage multiplier from perks
        damage *= self._get_perk_value('damage_mult', 1.0)

        # Relic damage bonuses
        damage *= self._get_relic_value('base_damage_mult', 1.0)
        damage *= self._get_relic_value('damage_mult', 1.0)
        damage += self._get_relic_value('flat_damage_bonus', 0)

        # Combo multiplier for damage (if perk owned)
        if self._has_perk_effect('combo_damages'):
            damage *= self.get_combo_multiplier()

        # Temp buffs
        for buff in self.temp_buffs:
            if 'damage_mult' in buff:
                damage *= buff['damage_mult']

        # Critical hit
        is_crit = False
        crit_chance = self._get_perk_value('crit_chance', 0)
        if crit_chance > 0 and random.random() < crit_chance:
            crit_mult = self._get_perk_value('crit_mult', 2.0)
            damage *= crit_mult
            is_crit = True

        return damage, is_crit

    def get_challenge_damage(self, base_damage=20):
        damage, is_crit = self.get_damage(base_damage)
        damage *= self._get_perk_value('challenge_damage_mult', 1.0)
        return damage, is_crit

    def take_damage(self, amount):
        # Defense perks
        amount *= self._get_perk_value('defense_mult', 1.0)

        # Temp buff defense
        for buff in self.temp_buffs:
            if 'defense_mult' in buff:
                amount *= buff['defense_mult']

        self.ghost_hp = self.display_hp
        self.hp = max(0, self.hp - amount)
        return amount

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def is_dead(self):
        return self.hp <= 0

    def can_revive(self):
        if self.used_revive:
            return False
        return 'rubber_duck' in self.relics

    def revive(self):
        self.used_revive = True
        self.hp = self.max_hp // 2
        self.display_hp = float(self.hp)
        self.ghost_hp = float(self.hp)

    def apply_lifesteal(self, damage_dealt):
        lifesteal = self._get_perk_value('lifesteal', 0)
        if lifesteal > 0:
            heal_amount = damage_dealt * lifesteal
            self.heal(heal_amount)

    def update(self, dt):
        # Combo decay
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
                self.combo_timer = 0.0

        # HP display lerp
        hp_diff = self.hp - self.display_hp
        self.display_hp += hp_diff * min(1.0, dt * 8)
        ghost_diff = self.display_hp - self.ghost_hp
        if ghost_diff < 0:
            self.ghost_hp += ghost_diff * min(1.0, dt * 3)

        # Input disable timer
        if self.input_disabled_timer > 0:
            self.input_disabled_timer -= dt

        # HP regen from perks
        regen = self._get_perk_value('hp_regen', 0)
        if regen > 0:
            self.regen_timer += dt
            if self.regen_timer >= 1.0:
                self.regen_timer -= 1.0
                self.heal(regen)

        # Auto-save
        now = time.time()
        if now - self.last_save_time >= SAVE_INTERVAL:
            self.save()
            self.last_save_time = now

    def get_auto_attack_interval(self):
        interval = self._get_perk_value('auto_attack_interval', 0)
        return interval

    def start_new_run(self):
        self.loc = 0.0
        self.total_loc = 0.0
        self.combo = 0
        self.combo_timer = 0.0
        self.wave = 1
        self.waves_completed = 0
        self.perks = []
        self.temp_buffs = []
        self.used_revive = False
        self.input_disabled_timer = 0.0
        self.auto_attack_timer = 0.0
        self.regen_timer = 0.0

        # Apply relic max HP bonuses
        self.max_hp = 100 + self._get_relic_value('max_hp_bonus', 0)
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.ghost_hp = float(self.max_hp)

    def add_perk(self, perk):
        self.perks.append(perk)
        # Apply immediate effects
        if 'max_hp_bonus' in perk.get('effect', {}):
            bonus = perk['effect']['max_hp_bonus']
            self.max_hp += bonus
            self.hp += bonus
            self.display_hp = float(self.hp)
            self.ghost_hp = float(self.hp)

    def add_relic(self, relic_id):
        if relic_id not in self.relics:
            self.relics.append(relic_id)

    def _get_perk_value(self, key, default):
        result = default
        for perk in self.perks:
            effect = perk.get('effect', {})
            if key in effect:
                val = effect[key]
                if isinstance(default, float) and isinstance(val, float):
                    if default == 1.0:
                        result *= val
                    else:
                        result += val
                elif isinstance(default, (int, float)):
                    result += val
                else:
                    result = val
        return result

    def _has_perk_effect(self, key):
        return any(key in p.get('effect', {}) for p in self.perks)

    def _get_relic_value(self, key, default):
        from upgrades import RELICS
        result = default
        for relic in RELICS:
            if relic['id'] in self.relics and key in relic.get('effect', {}):
                val = relic['effect'][key]
                if isinstance(default, float):
                    if default == 1.0:
                        result *= val
                    else:
                        result += val
                elif isinstance(default, (int, float)):
                    result += val
                else:
                    result = val
        return result

    def _check_milestones(self):
        for threshold, message in MILESTONES:
            if self.lifetime_loc >= threshold and threshold not in self.milestones_reached:
                self.milestones_reached.append(threshold)
                self.pending_milestones.append(message)

    def save(self):
        data = {
            "lifetime_loc": self.lifetime_loc,
            "milestones_reached": self.milestones_reached,
            "relics": self.relics,
            "runs_completed": self.runs_completed,
            "best_wave": self.best_wave,
            "total_enemies_killed": self.total_enemies_killed,
            "timestamp": time.time(),
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            self.lifetime_loc = data.get("lifetime_loc", 0.0)
            self.milestones_reached = data.get("milestones_reached", [])
            self.relics = data.get("relics", [])
            self.runs_completed = data.get("runs_completed", 0)
            self.best_wave = data.get("best_wave", 0)
            self.total_enemies_killed = data.get("total_enemies_killed", 0)
        except Exception:
            pass
