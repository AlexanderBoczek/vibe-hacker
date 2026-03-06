from dataclasses import dataclass


@dataclass
class Upgrade:
    id: str
    name: str
    category: str  # typing_efficiency, auto_typer, multiplier, one_time_boost
    description: str
    effect_value: float
    base_cost: float
    cost_multiplier: float
    unlock_at: float  # total LOC needed to reveal
    max_count: int  # -1 = unlimited

    def get_cost(self, count_owned):
        if self.category == "one_time_boost":
            return self.base_cost
        return self.base_cost * (self.cost_multiplier ** count_owned)

    def is_unlocked(self, total_loc):
        return total_loc >= self.unlock_at

    def can_buy(self, count_owned):
        if self.max_count != -1 and count_owned >= self.max_count:
            return False
        return True


UPGRADES = [
    # Typing Efficiency
    Upgrade("mech_keyboard", "Mechanical Keyboard", "typing_efficiency",
            "+1 char per correct keypress", 1, 50, 1.8, 0, -1),
    Upgrade("cherry_mx", "Cherry MX Switches", "typing_efficiency",
            "+3 chars per correct keypress", 3, 500, 2.0, 200, -1),
    Upgrade("ergo_layout", "Ergonomic Layout", "typing_efficiency",
            "+8 chars per correct keypress", 8, 5_000, 2.2, 2_000, -1),
    Upgrade("neural_interface", "Neural Interface", "typing_efficiency",
            "+25 chars per correct keypress", 25, 100_000, 2.5, 50_000, -1),

    # Auto-Typers
    Upgrade("intern", "Intern", "auto_typer",
            "0.5 LOC/sec", 0.5, 100, 1.15, 50, -1),
    Upgrade("junior_dev", "Junior Dev", "auto_typer",
            "3 LOC/sec", 3, 1_000, 1.15, 500, -1),
    Upgrade("senior_dev", "Senior Dev", "auto_typer",
            "15 LOC/sec", 15, 12_000, 1.15, 5_000, -1),
    Upgrade("ai_copilot", "AI Copilot", "auto_typer",
            "80 LOC/sec", 80, 150_000, 1.15, 50_000, -1),
    Upgrade("agi", "AGI", "auto_typer",
            "500 LOC/sec", 500, 2_000_000, 1.15, 500_000, -1),
    Upgrade("dyson_sphere", "Dyson Sphere", "auto_typer",
            "5000 LOC/sec", 5000, 50_000_000, 1.15, 5_000_000, -1),

    # Multipliers
    Upgrade("coffee", "Coffee", "multiplier",
            "1.5x all production", 1.5, 200, 3.0, 100, -1),
    Upgrade("energy_drinks", "Energy Drinks", "multiplier",
            "2x all production", 2.0, 5_000, 3.5, 2_000, -1),
    Upgrade("adderall", "Adderall", "multiplier",
            "3x all production", 3.0, 50_000, 4.0, 20_000, -1),
    Upgrade("the_zone", "\"The Zone\"", "multiplier",
            "5x all production", 5.0, 500_000, 5.0, 200_000, -1),
    Upgrade("time_dilation", "Time Dilation", "multiplier",
            "10x all production", 10.0, 10_000_000, 6.0, 5_000_000, -1),

    # One-time Boosts
    Upgrade("stack_overflow", "Stack Overflow Access", "one_time_boost",
            "2x permanent boost", 2.0, 300, 1.0, 150, 1),
    Upgrade("github_copilot", "GitHub Copilot", "one_time_boost",
            "3x permanent boost", 3.0, 3_000, 1.0, 1_500, 1),
    Upgrade("copied_prod", "Copied from Production", "one_time_boost",
            "5x permanent boost", 5.0, 30_000, 1.0, 15_000, 1),
    Upgrade("works_on_my_machine", "\"It Works On My Machine\"", "one_time_boost",
            "10x permanent boost", 10.0, 300_000, 1.0, 150_000, 1),
]

CATEGORY_NAMES = {
    "typing_efficiency": "Typing",
    "auto_typer": "Auto-Typers",
    "multiplier": "Multipliers",
    "one_time_boost": "Boosts",
}

CATEGORY_ORDER = ["typing_efficiency", "auto_typer", "multiplier", "one_time_boost"]
