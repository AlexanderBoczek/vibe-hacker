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
SAVE_INTERVAL = 30.0  # seconds


class GameState:
    def __init__(self):
        self.loc = 0.0
        self.total_loc = 0.0
        self.owned_upgrades = {}  # upgrade_id -> count
        self.milestones_reached = []
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_max_gap = 0.8  # seconds between correct keys
        self.loc_per_sec = 0.0
        self.last_save_time = time.time()
        self.pending_milestones = []  # queue for UI to consume
        self.auto_loc_accumulator = 0.0  # fractional LOC from auto-typers

    def add_loc(self, amount):
        self.loc += amount
        self.total_loc += amount
        self._check_milestones()

    def spend_loc(self, amount):
        if self.loc >= amount:
            self.loc -= amount
            return True
        return False

    def register_correct_key(self):
        self.combo += 1
        self.combo_timer = self.combo_max_gap

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

    def update(self, dt):
        # Combo decay
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
                self.combo_timer = 0.0

        # Auto-save
        now = time.time()
        if now - self.last_save_time >= SAVE_INTERVAL:
            self.save()
            self.last_save_time = now

    def _check_milestones(self):
        for threshold, message in MILESTONES:
            if self.total_loc >= threshold and threshold not in self.milestones_reached:
                self.milestones_reached.append(threshold)
                self.pending_milestones.append(message)

    def get_chars_per_press(self, upgrades_module):
        """Calculate total chars per correct keypress from typing efficiency upgrades."""
        base = 1
        for upg in upgrades_module.UPGRADES:
            if upg.category == "typing_efficiency":
                count = self.owned_upgrades.get(upg.id, 0)
                base += upg.effect_value * count
        return base

    def get_auto_loc_per_sec(self, upgrades_module):
        """Calculate passive LOC/sec from auto-typers."""
        total = 0.0
        for upg in upgrades_module.UPGRADES:
            if upg.category == "auto_typer":
                count = self.owned_upgrades.get(upg.id, 0)
                total += upg.effect_value * count
        return total

    def get_global_multiplier(self, upgrades_module):
        """Calculate total multiplier from multiplier and boost upgrades."""
        mult = 1.0
        for upg in upgrades_module.UPGRADES:
            if upg.category == "multiplier":
                count = self.owned_upgrades.get(upg.id, 0)
                for _ in range(count):
                    mult *= upg.effect_value
            elif upg.category == "one_time_boost":
                count = self.owned_upgrades.get(upg.id, 0)
                if count > 0:
                    mult *= upg.effect_value
        return mult

    def save(self):
        data = {
            "loc": self.loc,
            "total_loc": self.total_loc,
            "owned_upgrades": self.owned_upgrades,
            "milestones_reached": self.milestones_reached,
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
            self.loc = data.get("loc", 0.0)
            self.total_loc = data.get("total_loc", 0.0)
            self.owned_upgrades = data.get("owned_upgrades", {})
            self.milestones_reached = data.get("milestones_reached", [])
        except Exception:
            pass
