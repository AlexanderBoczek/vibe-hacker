import random
from enemy import Enemy
from game_state import TOTAL_WAVES


class BattleSystem:
    def __init__(self, game_state, effects, particles, renderer, sound_mgr):
        self.game_state = game_state
        self.effects = effects
        self.particles = particles
        self.renderer = renderer
        self.sound_mgr = sound_mgr
        self.enemy = None
        self.wave_clear = False
        self.wave_clear_timer = 0.0
        self.run_complete = False

    def start_wave(self, wave_number):
        self.enemy = Enemy(wave_number)
        self.wave_clear = False
        self.wave_clear_timer = 0.0
        self.run_complete = False
        self.game_state.temp_buffs = []
        self.effects.show_wave_text(f"WAVE {wave_number}")
        self.renderer.player_lines.clear()
        self.renderer.player_line_timers.clear()
        self.renderer.add_player_line(f"user@localhost:~$ Incoming threat: {self.enemy.name}", (0, 255, 100))

    def handle_mash_key(self, char):
        gs = self.game_state
        if gs.input_disabled_timer > 0:
            return

        # Mashing always works — typing text, building combo, earning LOC
        gs.register_correct_key()
        self.sound_mgr.play_click()
        self.renderer.add_mash_char()

        combo_mult = gs.get_combo_multiplier()
        loc_earned = combo_mult * 0.5
        gs.add_loc(loc_earned)

        # Only deal damage if enemy is active (not booting/dead)
        if not self.enemy or self.enemy.is_dead() or self.enemy.booting:
            return

        base_damage = 1
        damage, is_crit = gs.get_damage(base_damage)

        self.enemy.take_damage(damage)
        gs.apply_lifesteal(damage)

        # Visual feedback
        mid_x = self.renderer.enemy_panel.centerx
        hp_y = self.renderer.enemy_panel.y + 30
        self.particles.add_damage_number(
            mid_x + random.randint(-30, 30), hp_y,
            damage, is_player_damage=False, is_crit=is_crit
        )

        if is_crit:
            self.effects.trigger_hitlag(0.03)
            self.effects.flash_enemy()
            self.effects.add_trauma(0.3)
            self.sound_mgr.play_crit()
        else:
            self.effects.flash_enemy()
            self.effects.add_trauma(0.05)

        self._check_enemy_death()

    def handle_challenge_complete(self, result):
        gs = self.game_state
        if not self.enemy or self.enemy.is_dead():
            return

        action = result['action']
        command = result['command']

        if action == 'attack':
            base = 25
            damage, is_crit = gs.get_challenge_damage(base)
            self.enemy.take_damage(damage)
            gs.apply_lifesteal(damage)
            self.renderer.add_player_line(f"user@localhost:~$ {command}", (255, 60, 60))
            self.renderer.add_player_line(f"  [EXPLOIT] Dealt {int(damage)} damage!", (255, 100, 100))

            mid_x = self.renderer.enemy_panel.centerx
            hp_y = self.renderer.enemy_panel.y + 30
            self.particles.add_damage_number(
                mid_x + random.randint(-20, 20), hp_y,
                damage, is_player_damage=False, is_crit=is_crit
            )
            self.effects.flash_enemy()
            self.effects.add_trauma(0.2)
            if is_crit:
                self.effects.trigger_hitlag(0.05)
            self.sound_mgr.play_attack()

        elif action == 'defend':
            # Temporary defense buff
            gs.temp_buffs.append({'defense_mult': 0.5})
            self.renderer.add_player_line(f"user@localhost:~$ {command}", (60, 160, 255))
            self.renderer.add_player_line(f"  [FIREWALL] Defense boosted!", (100, 200, 255))
            self.sound_mgr.play_defend()

        elif action == 'hack':
            # Debuff enemy + buff self
            base = 15
            damage, is_crit = gs.get_challenge_damage(base)
            self.enemy.take_damage(damage)
            gs.heal(10)
            self.renderer.add_player_line(f"user@localhost:~$ {command}", (200, 60, 255))
            self.renderer.add_player_line(f"  [BACKDOOR] {int(damage)} dmg + 10 HP restored!", (220, 100, 255))

            mid_x = self.renderer.enemy_panel.centerx
            hp_y = self.renderer.enemy_panel.y + 30
            self.particles.add_damage_number(
                mid_x, hp_y, damage, is_player_damage=False, is_crit=is_crit
            )
            self.effects.flash_enemy()
            self.sound_mgr.play_hack()

        # LOC bonus for completing challenge
        combo_mult = gs.get_combo_multiplier()
        loc_bonus = 10 * combo_mult
        gs.add_loc(loc_bonus)

        self.particles.add_particles(
            self.renderer.player_panel.centerx,
            self.renderer.player_panel.centery,
            count=20, color=result['color']
        )

        self._check_enemy_death()

    def handle_enemy_attack(self, attack_result):
        if not attack_result:
            return

        gs = self.game_state
        damage = attack_result['damage']
        attack_type = attack_result['type']

        actual_damage = gs.take_damage(damage)

        # Enemy terminal line is already added by enemy.update()

        # Player feedback
        self.renderer.add_player_line(
            f"  [INCOMING] {attack_result['name']}: -{int(actual_damage)} HP",
            attack_result['color']
        )

        # Visual effects
        self.effects.flash_player(attack_result['color'])
        self.effects.add_trauma(0.15 + damage * 0.01)
        self.sound_mgr.play_damage()

        # Damage number on player
        mid_x = self.renderer.player_panel.centerx
        hp_y = self.renderer.player_panel.y + 30
        self.particles.add_damage_number(
            mid_x + random.randint(-20, 20), hp_y,
            actual_damage, is_player_damage=True
        )

        # Special attack effects
        if attack_type == 'phishing':
            steal = attack_result.get('steal_loc', 0.1)
            stolen = gs.loc * steal
            gs.loc = max(0, gs.loc - stolen)
            self.renderer.add_player_line(f"  [WARNING] {int(stolen)} LOC stolen!", (255, 200, 50))

        if attack_type == 'ransomware':
            disable_time = attack_result.get('disable_time', 2.0)
            gs.input_disabled_timer = disable_time
            self.renderer.add_player_line(
                f"  [LOCKED] Input disabled for {disable_time:.1f}s!", (255, 50, 50))

    def update(self, dt):
        if not self.enemy:
            return

        # Wave clear animation — stop updating enemy, wait for main loop to transition
        if self.wave_clear:
            self.wave_clear_timer += dt
            return

        # Enemy update
        attack_result = self.enemy.update(dt)
        if attack_result:
            self.handle_enemy_attack(attack_result)

        # Auto attack from perks
        interval = self.game_state.get_auto_attack_interval()
        if interval > 0:
            self.game_state.auto_attack_timer += dt
            if self.game_state.auto_attack_timer >= interval:
                self.game_state.auto_attack_timer -= interval
                if not self.enemy.is_dead() and not self.enemy.booting:
                    damage, is_crit = self.game_state.get_damage(5)
                    self.enemy.take_damage(damage)
                    self.renderer.add_player_line(
                        f"  [AUTO] Cron job dealt {int(damage)} damage", DIM_GREEN)
                    mid_x = self.renderer.enemy_panel.centerx
                    hp_y = self.renderer.enemy_panel.y + 30
                    self.particles.add_damage_number(
                        mid_x, hp_y, damage, is_crit=is_crit)
                    self._check_enemy_death()

    def _check_enemy_death(self):
        if self.enemy and self.enemy.is_dead() and not self.wave_clear:
            self.wave_clear = True
            self.wave_clear_timer = 0.0
            self.game_state.total_enemies_killed += 1
            self.game_state.waves_completed = self.game_state.wave

            # LOC bonus for kill
            kill_bonus = 50 * self.game_state.wave
            kill_mult = 1.0
            for perk in self.game_state.perks:
                if 'loc_kill_bonus' in perk.get('effect', {}):
                    kill_mult *= perk['effect']['loc_kill_bonus']
            self.game_state.add_loc(kill_bonus * kill_mult)

            # Update best wave
            if self.game_state.wave > self.game_state.best_wave:
                self.game_state.best_wave = self.game_state.wave

            # Effects
            self.effects.flash_screen((255, 255, 255), 0.15)
            self.effects.trigger_glitch(0.8, 0.5)
            self.effects.add_trauma(0.5)
            self.sound_mgr.play_wave_clear()

            self.renderer.add_player_line(
                f"  [VICTORY] {self.enemy.name} defeated! +{int(kill_bonus * kill_mult)} LOC",
                (255, 215, 0))

            # Check if run complete
            if self.game_state.wave >= TOTAL_WAVES:
                self.run_complete = True

    def is_wave_clear(self):
        return self.wave_clear and self.wave_clear_timer > 2.0

    def is_run_complete(self):
        return self.run_complete


DIM_GREEN = (0, 100, 60)
