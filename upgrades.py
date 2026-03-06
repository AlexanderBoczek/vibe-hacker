import random

# --- PERKS (chosen between waves, free, 1 of 3) ---

PERK_POOL = [
    {
        'id': 'typing_damage_20',
        'name': 'Buffer Overflow',
        'description': '+20% typing damage',
        'effect': {'damage_mult': 1.2},
    },
    {
        'id': 'typing_damage_35',
        'name': 'Stack Smash',
        'description': '+35% typing damage',
        'effect': {'damage_mult': 1.35},
    },
    {
        'id': 'firewall',
        'name': 'Firewall',
        'description': 'Reduce incoming damage by 15%',
        'effect': {'defense_mult': 0.85},
    },
    {
        'id': 'hardened_kernel',
        'name': 'Hardened Kernel',
        'description': 'Reduce incoming damage by 25%',
        'effect': {'defense_mult': 0.75},
    },
    {
        'id': 'auto_attack',
        'name': 'Cron Job',
        'description': 'Auto-attack every 5 seconds',
        'effect': {'auto_attack_interval': 5.0},
    },
    {
        'id': 'combo_window',
        'name': 'Debounce',
        'description': 'Combo window extended by 0.5s',
        'effect': {'combo_window_bonus': 0.5},
    },
    {
        'id': 'crit_chance',
        'name': 'Zero-Day Exploit',
        'description': '15% critical hit chance (2x damage)',
        'effect': {'crit_chance': 0.15},
    },
    {
        'id': 'crit_chance_2',
        'name': 'Race Condition',
        'description': '10% critical hit chance (3x damage)',
        'effect': {'crit_chance': 0.10, 'crit_mult': 3.0},
    },
    {
        'id': 'loc_magnet',
        'name': 'Git Blame',
        'description': '+50% LOC per kill',
        'effect': {'loc_kill_bonus': 1.5},
    },
    {
        'id': 'vampiric',
        'name': 'Memory Leak',
        'description': 'Heal 5% of damage dealt',
        'effect': {'lifesteal': 0.05},
    },
    {
        'id': 'typing_speed',
        'name': 'Mechanical Keyboard',
        'description': '+2 damage per keypress',
        'effect': {'flat_damage_bonus': 2},
    },
    {
        'id': 'challenge_bonus',
        'name': 'Compiler Optimization',
        'description': '+50% damage from typing challenges',
        'effect': {'challenge_damage_mult': 1.5},
    },
    {
        'id': 'regen',
        'name': 'Health Check',
        'description': 'Regenerate 1 HP per second',
        'effect': {'hp_regen': 1.0},
    },
    {
        'id': 'max_hp_up',
        'name': 'RAM Upgrade',
        'description': '+25 max HP',
        'effect': {'max_hp_bonus': 25},
    },
    {
        'id': 'double_loc',
        'name': 'Copy-Paste',
        'description': '2x LOC earned',
        'effect': {'loc_mult': 2.0},
    },
    {
        'id': 'combo_damage',
        'name': 'Pipeline',
        'description': 'Combo multiplier also boosts damage',
        'effect': {'combo_damages': True},
    },
]


def get_perk_choices(owned_perk_ids, count=3):
    available = [p for p in PERK_POOL if p['id'] not in owned_perk_ids]
    if len(available) <= count:
        return list(available)
    return random.sample(available, count)


# --- SHOP ITEMS (spend LOC between waves) ---

def get_shop_items(game_state, wave_number):
    items = []

    # Heal
    if game_state.hp < game_state.max_hp:
        heal_cost = int(50 * wave_number)
        heal_amount = min(30, game_state.max_hp - game_state.hp)
        items.append({
            'id': 'heal',
            'name': 'Patch System',
            'description': f'Restore {heal_amount} HP',
            'cost': heal_cost,
            'action': 'heal',
            'value': heal_amount,
        })

    # Full heal
    if game_state.hp < game_state.max_hp * 0.7:
        full_heal_cost = int(200 * wave_number)
        items.append({
            'id': 'full_heal',
            'name': 'System Restore',
            'description': f'Restore to full HP',
            'cost': full_heal_cost,
            'action': 'full_heal',
        })

    # Temporary buffs
    items.append({
        'id': 'temp_damage',
        'name': 'Energy Drink',
        'description': '+50% damage next wave',
        'cost': int(100 * wave_number),
        'action': 'temp_buff',
        'value': {'damage_mult': 1.5},
    })

    items.append({
        'id': 'temp_defense',
        'name': 'VPN Shield',
        'description': '-30% damage taken next wave',
        'cost': int(80 * wave_number),
        'action': 'temp_buff',
        'value': {'defense_mult': 0.7},
    })

    items.append({
        'id': 'temp_speed',
        'name': 'Caffeine Injection',
        'description': 'Faster challenge spawns next wave',
        'cost': int(60 * wave_number),
        'action': 'temp_buff',
        'value': {'challenge_speed': 1.5},
    })

    # Max HP upgrade
    items.append({
        'id': 'max_hp',
        'name': 'Install More RAM',
        'description': '+10 max HP permanently',
        'cost': int(150 * wave_number),
        'action': 'max_hp',
        'value': 10,
    })

    return items


# --- RELICS (permanent, earned by completing all waves) ---

RELICS = [
    {
        'id': 'caffeine_iv',
        'name': 'Caffeine IV',
        'description': '+5% base typing speed',
        'effect': {'base_damage_mult': 1.05},
    },
    {
        'id': 'rubber_duck',
        'name': 'Rubber Duck',
        'description': 'One free revive per run',
        'effect': {'free_revive': True},
    },
    {
        'id': 'stack_overflow',
        'name': 'Stack Overflow',
        'description': 'Typing challenges show first 3 chars dimly',
        'effect': {'challenge_hint': True},
    },
    {
        'id': 'dark_theme',
        'name': 'Dark Theme',
        'description': '+10% damage at all times',
        'effect': {'damage_mult': 1.1},
    },
    {
        'id': 'mechanical_kb',
        'name': 'Cherry MX Blues',
        'description': '+3 flat damage per keypress',
        'effect': {'flat_damage_bonus': 3},
    },
    {
        'id': 'sudo',
        'name': 'sudo Mode',
        'description': '+15 max HP each run',
        'effect': {'max_hp_bonus': 15},
    },
]


# Milestone unlocks (reusing existing thresholds)
from game_state import MILESTONES

MILESTONE_UNLOCKS = {
    100: "Script Kiddie enemy type unlocked",
    1_000: "New attack commands available",
    10_000: "Advanced enemy patterns",
    100_000: "Elite enemy types",
    1_000_000: "Ultimate abilities",
    10_000_000: "Legendary relics",
}
