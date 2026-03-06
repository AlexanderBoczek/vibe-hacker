import random
import math
import pygame


class ScreenEffects:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Screen shake
        self.trauma = 0.0

        # Flash effects
        self.player_flash = 0.0  # red flash when taking damage
        self.player_flash_color = (255, 0, 0)
        self.enemy_flash = 0.0   # white flash when dealing damage
        self.screen_flash = 0.0  # full screen flash (wave clear)
        self.screen_flash_color = (255, 255, 255)

        # CRT scanline overlay
        self.crt_overlay = self._make_crt_overlay(screen_w, screen_h)

        # Hitlag (freeze frames)
        self.hitlag_timer = 0.0

        # Glitch effect
        self.glitch_timer = 0.0
        self.glitch_intensity = 0.0
        self.glitch_blocks = []

        # Panel glow
        self.player_hp_ratio = 1.0
        self.enemy_hp_ratio = 1.0

        # Idle breathing
        self.breath_timer = 0.0

        # Wave text
        self.wave_text = ""
        self.wave_text_timer = 0.0
        self.wave_text_scale = 1.0
        self.wave_font = pygame.font.Font(None, 96)

        # Death sequence
        self.death_active = False
        self.death_timer = 0.0
        self.death_lines = []
        self.game_over_text = ""
        self.game_over_char_idx = 0
        self.game_over_timer = 0.0

    def _make_crt_overlay(self, w, h):
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(overlay, (0, 0, 0, 25), (0, y), (w, y))
        return overlay

    def resize(self, w, h):
        self.screen_w = w
        self.screen_h = h
        self.crt_overlay = self._make_crt_overlay(w, h)

    def add_trauma(self, amount):
        self.trauma = min(1.0, self.trauma + amount)

    def flash_player(self, color=(255, 0, 0)):
        self.player_flash = 0.15
        self.player_flash_color = color

    def flash_enemy(self):
        self.enemy_flash = 0.1

    def flash_screen(self, color=(255, 255, 255), duration=0.1):
        self.screen_flash = duration
        self.screen_flash_color = color

    def trigger_hitlag(self, duration=0.03):
        self.hitlag_timer = duration

    def trigger_glitch(self, intensity=0.5, duration=0.3):
        self.glitch_timer = duration
        self.glitch_intensity = intensity
        self.glitch_blocks = []
        count = int(intensity * 15)
        for _ in range(count):
            self.glitch_blocks.append({
                'x': random.randint(0, self.screen_w),
                'y': random.randint(0, self.screen_h),
                'w': random.randint(20, 200),
                'h': random.randint(3, 20),
                'offset_x': random.randint(-30, 30),
                'color': random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                         (255, 255, 0), (0, 0, 0)]),
            })

    def show_wave_text(self, text):
        self.wave_text = text
        self.wave_text_timer = 2.0
        self.wave_text_scale = 1.5

    def start_death_sequence(self):
        self.death_active = True
        self.death_timer = 0.0
        self.death_lines = []
        self.game_over_text = "CONNECTION TERMINATED"
        self.game_over_char_idx = 0
        self.game_over_timer = 0.0

    def update(self, dt):
        # Trauma decay
        self.trauma = max(0, self.trauma - dt * 2.5)

        # Flash decay
        self.player_flash = max(0, self.player_flash - dt)
        self.enemy_flash = max(0, self.enemy_flash - dt)
        self.screen_flash = max(0, self.screen_flash - dt)

        # Hitlag
        if self.hitlag_timer > 0:
            self.hitlag_timer -= dt
            return True  # Signal to freeze game logic

        # Glitch
        self.glitch_timer = max(0, self.glitch_timer - dt)

        # Breathing
        self.breath_timer += dt

        # Wave text
        if self.wave_text_timer > 0:
            self.wave_text_timer -= dt
            # Scale bounces from 1.5 to 1.0
            t = 1.0 - (self.wave_text_timer / 2.0)
            self.wave_text_scale = 1.0 + max(0, 0.5 * (1.0 - t * 3))

        # Death sequence
        if self.death_active:
            self.death_timer += dt
            if self.death_timer < 2.0:
                # Red error text flood
                if random.random() < 0.3:
                    errors = [
                        "ERROR: Stack overflow",
                        "FATAL: Memory corruption detected",
                        "CRITICAL: Firewall breached",
                        "ERROR: Connection refused",
                        "FATAL: Segmentation fault (core dumped)",
                        "ERROR: Permission denied",
                        "CRITICAL: Root access revoked",
                        "FATAL: System compromised",
                    ]
                    self.death_lines.append(random.choice(errors))
                    if len(self.death_lines) > 40:
                        self.death_lines = self.death_lines[-40:]
            elif self.death_timer < 3.0:
                # Glitch corruption
                self.glitch_intensity = min(1.0, (self.death_timer - 2.0) * 3)
            elif self.death_timer < 3.5:
                pass  # Black screen
            else:
                # Type out game over text
                self.game_over_timer += dt
                if self.game_over_timer >= 0.08:
                    self.game_over_timer = 0
                    if self.game_over_char_idx < len(self.game_over_text):
                        self.game_over_char_idx += 1

        return False

    def get_shake_offset(self):
        if self.trauma <= 0:
            return 0, 0
        intensity = self.trauma ** 2 * 10
        ox = random.uniform(-intensity, intensity)
        oy = random.uniform(-intensity, intensity)
        return int(ox), int(oy)

    def get_breath_alpha(self):
        return 0.95 + 0.05 * math.sin(self.breath_timer * 0.8)

    def draw_crt_overlay(self, surface):
        surface.blit(self.crt_overlay, (0, 0))

    def draw_panel_flash(self, surface, panel_rect, is_player):
        if is_player and self.player_flash > 0:
            alpha = int((self.player_flash / 0.15) * 60)
            flash_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            flash_surf.fill((*self.player_flash_color, alpha))
            surface.blit(flash_surf, panel_rect.topleft)
        elif not is_player and self.enemy_flash > 0:
            alpha = int((self.enemy_flash / 0.1) * 80)
            flash_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, panel_rect.topleft)

    def draw_screen_flash(self, surface):
        if self.screen_flash > 0:
            alpha = int((self.screen_flash / 0.1) * 100)
            alpha = min(255, alpha)
            flash_surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            flash_surf.fill((*self.screen_flash_color, alpha))
            surface.blit(flash_surf, (0, 0))

    def draw_glitch(self, surface):
        if self.glitch_timer <= 0:
            return
        for block in self.glitch_blocks:
            if random.random() < self.glitch_intensity:
                rect = pygame.Rect(block['x'] + block['offset_x'], block['y'],
                                   block['w'], block['h'])
                pygame.draw.rect(surface, block['color'], rect)

    def draw_wave_text(self, surface):
        if self.wave_text_timer <= 0:
            return
        alpha = min(255, int(self.wave_text_timer * 255))
        text_surf = self.wave_font.render(self.wave_text, True, (0, 255, 100))
        if self.wave_text_scale != 1.0:
            w = int(text_surf.get_width() * self.wave_text_scale)
            h = int(text_surf.get_height() * self.wave_text_scale)
            text_surf = pygame.transform.scale(text_surf, (w, h))
        text_surf.set_alpha(alpha)
        x = self.screen_w // 2 - text_surf.get_width() // 2
        y = self.screen_h // 2 - text_surf.get_height() // 2
        surface.blit(text_surf, (x, y))

    def draw_panel_glow(self, surface, panel_rect, is_player, hp_ratio):
        color = (0, 255, 100) if is_player else (255, 60, 60)
        intensity = int(hp_ratio * 40 + 10)
        t = pygame.time.get_ticks() / 1000.0
        pulse = int(math.sin(t * 2) * 8)
        intensity = max(5, intensity + pulse)

        glow_surf = pygame.Surface((panel_rect.w + 4, panel_rect.h + 4), pygame.SRCALPHA)
        glow_color = (color[0], color[1], color[2], intensity)
        pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), 3, border_radius=2)
        surface.blit(glow_surf, (panel_rect.x - 2, panel_rect.y - 2))

    def draw_death_sequence(self, surface):
        if not self.death_active:
            return False

        if self.death_timer < 2.0:
            # Red error flood
            font = pygame.font.Font(None, 20)
            y = 10
            for line in self.death_lines[-30:]:
                text_surf = font.render(line, True, (255, 40, 40))
                surface.blit(text_surf, (10, y))
                y += 18
            return True

        if self.death_timer < 3.0:
            # Glitch corruption
            self.draw_glitch(surface)
            return True

        if self.death_timer < 3.5:
            # Black
            surface.fill((0, 0, 0))
            return True

        # Game over text
        surface.fill((0, 0, 0))
        if self.game_over_char_idx > 0:
            font = pygame.font.Font(None, 64)
            display_text = self.game_over_text[:self.game_over_char_idx]
            text_surf = font.render(display_text, True, (255, 60, 60))
            x = self.screen_w // 2 - text_surf.get_width() // 2
            y = self.screen_h // 2 - text_surf.get_height() // 2
            surface.blit(text_surf, (x, y))

            # Blinking cursor after text
            if self.game_over_char_idx >= len(self.game_over_text):
                if int(pygame.time.get_ticks() / 500) % 2 == 0:
                    cursor_x = x + text_surf.get_width() + 4
                    pygame.draw.rect(surface, (255, 60, 60),
                                     (cursor_x, y, 16, text_surf.get_height()))

                # Show restart prompt
                small_font = pygame.font.Font(None, 28)
                prompt = small_font.render("Press any key to restart", True, (150, 40, 40))
                surface.blit(prompt, (self.screen_w // 2 - prompt.get_width() // 2,
                                      self.screen_h // 2 + 60))
        return True
