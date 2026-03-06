import random
import math


ENEMY_ATTACK_TYPES = {
    "ddos": {
        "name": "DDoS",
        "damage_mult": 0.5,
        "duration": 3.0,
        "tick_rate": 0.3,
        "message": "LAUNCHING DDoS ATTACK...",
        "color": (255, 100, 100),
    },
    "sql_injection": {
        "name": "SQL Injection",
        "damage_mult": 2.5,
        "duration": 0,
        "tick_rate": 0,
        "message": "'; DROP TABLE users; --",
        "color": (255, 200, 50),
    },
    "phishing": {
        "name": "Phishing",
        "damage_mult": 0.0,
        "duration": 0,
        "tick_rate": 0,
        "steal_loc": 0.1,
        "message": "PHISHING: Stealing LOC...",
        "color": (200, 100, 255),
    },
    "ransomware": {
        "name": "Ransomware",
        "damage_mult": 1.0,
        "duration": 0,
        "tick_rate": 0,
        "disable_time": 2.0,
        "message": "ENCRYPTING YOUR FILES...",
        "color": (255, 50, 50),
    },
}

ENEMY_TEMPLATES = [
    {
        "name": "Script Kiddie",
        "title": "Novice Hacker",
        "base_hp": 100,
        "attack_interval": 3.0,
        "base_damage": 5,
        "attacks": ["sql_injection"],
        "color": (200, 50, 50),
    },
    {
        "name": "Bot Network",
        "title": "Automated Threat",
        "base_hp": 150,
        "attack_interval": 2.5,
        "base_damage": 7,
        "attacks": ["ddos", "sql_injection"],
        "color": (220, 80, 40),
    },
    {
        "name": "Black Hat",
        "title": "Elite Hacker",
        "base_hp": 200,
        "attack_interval": 2.0,
        "base_damage": 10,
        "attacks": ["sql_injection", "phishing"],
        "color": (255, 60, 60),
    },
    {
        "name": "APT Group",
        "title": "Advanced Persistent Threat",
        "base_hp": 300,
        "attack_interval": 1.8,
        "base_damage": 12,
        "attacks": ["ddos", "sql_injection", "phishing"],
        "color": (255, 40, 80),
    },
    {
        "name": "Zero Day",
        "title": "Unknown Exploit",
        "base_hp": 400,
        "attack_interval": 1.5,
        "base_damage": 15,
        "attacks": ["sql_injection", "ransomware", "phishing"],
        "color": (255, 20, 20),
    },
    {
        "name": "State Actor",
        "title": "Nation-State Hacker",
        "base_hp": 500,
        "attack_interval": 1.2,
        "base_damage": 20,
        "attacks": ["ddos", "sql_injection", "phishing", "ransomware"],
        "color": (200, 0, 0),
    },
]

ENEMY_TERMINAL_LINES = [
    "root@evil:~# scanning network...",
    "root@evil:~# vulnerability found!",
    "root@evil:~# deploying payload...",
    "root@evil:~# cracking password hash...",
    "root@evil:~# bypassing firewall...",
    "root@evil:~# escalating privileges...",
    "root@evil:~# exfiltrating data...",
    "root@evil:~# injecting shellcode...",
    "root@evil:~# spawning reverse shell...",
    "root@evil:~# pivoting to next target...",
    "root@evil:~# installing rootkit...",
    "root@evil:~# wiping logs...",
]


class Enemy:
    def __init__(self, wave_number):
        self.wave = wave_number
        template_idx = min(wave_number - 1, len(ENEMY_TEMPLATES) - 1)
        template = ENEMY_TEMPLATES[template_idx]

        self.name = template["name"]
        self.title = template["title"]
        self.color = template["color"]
        self.attacks = template["attacks"]

        # Scale stats with wave
        wave_scale = 1.0 + (wave_number - 1) * 0.3
        self.max_hp = int(template["base_hp"] * wave_scale)
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.ghost_hp = float(self.max_hp)
        self.base_damage = template["base_damage"] * wave_scale
        self.attack_interval = max(0.8, template["attack_interval"] - wave_number * 0.05)

        self.attack_timer = self.attack_interval
        self.telegraph_timer = 0.0
        self.is_telegraphing = False
        self.current_attack = None
        self.ddos_timer = 0.0
        self.ddos_tick_timer = 0.0

        # Terminal display
        self.terminal_lines = []
        self.line_timer = 0.0
        self.line_interval = 1.5

        # Boot sequence
        self.booting = True
        self.boot_lines = self._generate_boot_sequence()
        self.boot_index = 0
        self.boot_timer = 0.0
        self.boot_char_index = 0

        # Death animation
        self.dying = False
        self.death_timer = 0.0

    def _generate_boot_sequence(self):
        lines = [
            "BIOS POST... OK",
            f"Loading kernel... v{self.wave}.{random.randint(0,9)}.{random.randint(0,99)}",
            "Initializing network stack...",
            "Mounting encrypted filesystem...",
            f"Connecting to C2 server...",
            f"Target acquired: YOU",
            "",
            f"=== {self.name.upper()} ===",
            f"    {self.title}",
            "",
        ]
        return lines

    def update(self, dt):
        # HP display lerp
        hp_diff = self.hp - self.display_hp
        self.display_hp += hp_diff * min(1.0, dt * 8)
        ghost_diff = self.display_hp - self.ghost_hp
        if ghost_diff < 0:
            self.ghost_hp += ghost_diff * min(1.0, dt * 3)

        if self.dying:
            self.death_timer += dt
            return None

        if self.booting:
            self.boot_timer += dt
            if self.boot_timer >= 0.05:
                self.boot_timer = 0
                if self.boot_index < len(self.boot_lines):
                    line = self.boot_lines[self.boot_index]
                    if self.boot_char_index < len(line):
                        self.boot_char_index += 1
                    else:
                        self.terminal_lines.append(line)
                        self.boot_index += 1
                        self.boot_char_index = 0
                else:
                    self.booting = False
            return None

        # Ambient terminal lines
        self.line_timer += dt
        if self.line_timer >= self.line_interval:
            self.line_timer = 0
            self.terminal_lines.append(random.choice(ENEMY_TERMINAL_LINES))
            if len(self.terminal_lines) > 30:
                self.terminal_lines = self.terminal_lines[-30:]

        # DDoS sustained damage
        if self.ddos_timer > 0:
            self.ddos_timer -= dt
            self.ddos_tick_timer -= dt
            if self.ddos_tick_timer <= 0:
                self.ddos_tick_timer = ENEMY_ATTACK_TYPES["ddos"]["tick_rate"]
                return self._make_attack_result("ddos")
            return None

        # Attack timer
        self.attack_timer -= dt

        # Telegraph phase
        if not self.is_telegraphing and self.attack_timer <= 0.5:
            self.is_telegraphing = True
            self.telegraph_timer = 0.5
            self.current_attack = random.choice(self.attacks)

        if self.is_telegraphing:
            self.telegraph_timer -= dt
            if self.telegraph_timer <= 0:
                self.is_telegraphing = False
                self.attack_timer = self.attack_interval
                attack_type = self.current_attack
                self.current_attack = None

                if attack_type == "ddos":
                    info = ENEMY_ATTACK_TYPES["ddos"]
                    self.ddos_timer = info["duration"]
                    self.ddos_tick_timer = info["tick_rate"]
                    self.terminal_lines.append(info["message"])
                    return self._make_attack_result("ddos")
                else:
                    info = ENEMY_ATTACK_TYPES[attack_type]
                    self.terminal_lines.append(info["message"])
                    return self._make_attack_result(attack_type)

        return None

    def _make_attack_result(self, attack_type):
        info = ENEMY_ATTACK_TYPES[attack_type]
        damage = self.base_damage * info["damage_mult"]
        result = {
            "type": attack_type,
            "damage": damage,
            "name": info["name"],
            "message": info["message"],
            "color": info["color"],
        }
        if attack_type == "phishing":
            result["steal_loc"] = info["steal_loc"]
        if attack_type == "ransomware":
            result["disable_time"] = info["disable_time"]
        return result

    def take_damage(self, amount):
        self.ghost_hp = self.display_hp
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.dying = True
            self.terminal_lines.append("SEGMENTATION FAULT")
            self.terminal_lines.append("KERNEL PANIC - not syncing")
            self.terminal_lines.append("---[ end Kernel panic ]---")

    def is_dead(self):
        return self.hp <= 0

    def get_boot_current_line(self):
        if self.booting and self.boot_index < len(self.boot_lines):
            line = self.boot_lines[self.boot_index]
            return line[:self.boot_char_index]
        return None
