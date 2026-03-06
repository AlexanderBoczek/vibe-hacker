import pygame
import math
import random
from code_generator import (
    CodeGenerator, TOKEN_KEYWORD, TOKEN_STRING, TOKEN_COMMENT,
    TOKEN_NUMBER, TOKEN_OPERATOR, TOKEN_DEFAULT,
)

# Layout constants
SCREEN_W = 1280
SCREEN_H = 720
TOP_MARGIN = 10
BOTTOM_BAR_H = 50
PANEL_GAP = 8
PANEL_TOP = TOP_MARGIN
PANEL_BOTTOM_Y = SCREEN_H - BOTTOM_BAR_H

# Colors
BG_COLOR = (5, 5, 10)
PLAYER_PANEL_BG = (8, 15, 10)
ENEMY_PANEL_BG = (15, 8, 10)
GREEN = (0, 220, 0)
BRIGHT_GREEN = (0, 255, 100)
DIM_GREEN = (0, 100, 60)
RED = (255, 60, 60)
BRIGHT_RED = (255, 100, 100)
DIM_RED = (150, 40, 40)
WHITE = (200, 200, 200)
GOLD = (255, 215, 0)
CYAN = (0, 200, 220)
BAR_BG = (30, 30, 30)
HP_GREEN = (0, 200, 80)
HP_RED = (200, 40, 40)
HP_GHOST = (100, 200, 100, 128)
BOTTOM_BAR_BG = (10, 10, 15)

TOKEN_COLORS = {
    TOKEN_KEYWORD: (0, 255, 100),
    TOKEN_STRING: (0, 200, 220),
    TOKEN_COMMENT: (0, 100, 60),
    TOKEN_NUMBER: (200, 200, 0),
    TOKEN_OPERATOR: (180, 180, 180),
    TOKEN_DEFAULT: (0, 220, 0),
}


def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{int(n)}"


class Renderer:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.mono_font = pygame.font.SysFont("monospace", 14)
        self.terminal_font = pygame.font.SysFont("monospace", 16)
        self.ui_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.combo_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 20)
        self.perk_font = pygame.font.Font(None, 28)

        self._calc_layout()

        # Player terminal state
        # Each line is a list of (char, color) tuples for syntax highlighting
        self.player_lines = []
        self.player_line_timers = []
        self.max_terminal_lines = 40
        self.current_mash_chars = []  # list of (char, color) for current line
        self.max_line_len = 60
        self.code_gen = CodeGenerator()

        # Enemy terminal state is driven by enemy object

        # Cursor blink
        self.cursor_timer = 0.0

        # Combo display
        self.combo_display_size = 1.0
        self.combo_last = 0

    def _calc_layout(self):
        panel_w = (self.screen_w - PANEL_GAP) // 2
        panel_h = self.screen_h - BOTTOM_BAR_H - TOP_MARGIN
        self.player_panel = pygame.Rect(0, PANEL_TOP, panel_w, panel_h)
        self.enemy_panel = pygame.Rect(panel_w + PANEL_GAP, PANEL_TOP, panel_w, panel_h)
        self.bottom_bar = pygame.Rect(0, self.screen_h - BOTTOM_BAR_H,
                                       self.screen_w, BOTTOM_BAR_H)
        self.hp_bar_h = 20
        self.hp_bar_margin = 10
        self.terminal_start_y = 60  # inside panel, after HP bar area

    def resize(self, w, h):
        self.screen_w = w
        self.screen_h = h
        self._calc_layout()

    def add_player_line(self, text, color=GREEN):
        # Convert plain text to list of (char, color) tuples
        chars = [(ch, color) for ch in text]
        self.player_lines.append(chars)
        self.player_line_timers.append(5.0)
        if len(self.player_lines) > self.max_terminal_lines:
            self.player_lines.pop(0)
            self.player_line_timers.pop(0)

    def add_mash_char(self):
        # Pull next character from real code templates
        chars_with_tokens, lines_completed = self.code_gen.advance(1)
        if chars_with_tokens:
            ch, token_type = chars_with_tokens[0]
            color = TOKEN_COLORS.get(token_type, GREEN)
            self.current_mash_chars.append((ch, color))

        if lines_completed > 0 or len(self.current_mash_chars) >= self.max_line_len:
            # Commit current line
            if self.current_mash_chars:
                self.player_lines.append(list(self.current_mash_chars))
                self.player_line_timers.append(5.0)
                if len(self.player_lines) > self.max_terminal_lines:
                    self.player_lines.pop(0)
                    self.player_line_timers.pop(0)
                self.current_mash_chars = []

    def _draw_colored_chars(self, surface, chars, x, y, fade=1.0):
        """Draw a list of (char, color) tuples. Returns x position after last char."""
        for ch, color in chars:
            faded = (int(color[0] * fade), int(color[1] * fade), int(color[2] * fade))
            ch_surf = self.mono_font.render(ch, True, faded)
            surface.blit(ch_surf, (x, y))
            x += ch_surf.get_width()
        return x

    def update(self, dt):
        self.cursor_timer += dt
        for i in range(len(self.player_line_timers)):
            self.player_line_timers[i] -= dt * 0.2

    def draw_panels(self, surface, game_state, enemy, effects):
        # Player panel
        pygame.draw.rect(surface, PLAYER_PANEL_BG, self.player_panel)
        effects.draw_panel_glow(surface, self.player_panel, True,
                                game_state.hp / game_state.max_hp)
        effects.draw_panel_flash(surface, self.player_panel, True)

        # Enemy panel
        pygame.draw.rect(surface, ENEMY_PANEL_BG, self.enemy_panel)
        if enemy:
            effects.draw_panel_glow(surface, self.enemy_panel, False,
                                    enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0)
        effects.draw_panel_flash(surface, self.enemy_panel, False)

    def draw_hp_bars(self, surface, game_state, enemy):
        # Player HP bar
        self._draw_hp_bar(surface, self.player_panel.x + self.hp_bar_margin,
                          self.player_panel.y + 8,
                          self.player_panel.w - self.hp_bar_margin * 2,
                          self.hp_bar_h,
                          game_state.hp, game_state.max_hp,
                          game_state.display_hp, game_state.ghost_hp,
                          HP_GREEN, "SYSTEM INTEGRITY", True)

        # Enemy HP bar
        if enemy:
            self._draw_hp_bar(surface, self.enemy_panel.x + self.hp_bar_margin,
                              self.enemy_panel.y + 8,
                              self.enemy_panel.w - self.hp_bar_margin * 2,
                              self.hp_bar_h,
                              enemy.hp, enemy.max_hp,
                              enemy.display_hp, enemy.ghost_hp,
                              HP_RED, f"{enemy.name}", False)

    def _draw_hp_bar(self, surface, x, y, w, h, hp, max_hp, display_hp, ghost_hp,
                     color, label, is_player):
        # Label
        label_surf = self.small_font.render(label, True,
                                             BRIGHT_GREEN if is_player else BRIGHT_RED)
        surface.blit(label_surf, (x, y - 2))
        hp_text = f"{int(max(0, hp))}/{int(max_hp)}"
        hp_surf = self.small_font.render(hp_text, True, WHITE)
        surface.blit(hp_surf, (x + w - hp_surf.get_width(), y - 2))

        bar_y = y + 16
        # Background
        pygame.draw.rect(surface, BAR_BG, (x, bar_y, w, h), border_radius=3)

        # Ghost bar (previous HP, drains slowly)
        if max_hp > 0:
            ghost_ratio = max(0, min(1, ghost_hp / max_hp))
            ghost_w = int(w * ghost_ratio)
            if ghost_w > 0:
                ghost_color = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.rect(surface, ghost_color, (x, bar_y, ghost_w, h), border_radius=3)

            # Current HP bar (smooth lerp)
            display_ratio = max(0, min(1, display_hp / max_hp))
            bar_w = int(w * display_ratio)
            if bar_w > 0:
                pygame.draw.rect(surface, color, (x, bar_y, bar_w, h), border_radius=3)

        # Border
        pygame.draw.rect(surface, color, (x, bar_y, w, h), 1, border_radius=3)

    def draw_player_terminal(self, surface, typing_challenge):
        clip = surface.get_clip()
        term_rect = pygame.Rect(self.player_panel.x + 5,
                                self.player_panel.y + self.terminal_start_y,
                                self.player_panel.w - 10,
                                self.player_panel.h - self.terminal_start_y - 5)
        surface.set_clip(term_rect)

        # Reserve space: current mash line at very bottom, then completed lines above
        bottom_y = term_rect.bottom - 18

        # Draw current mash chars (syntax highlighted) + blinking cursor at bottom
        cursor_x = term_rect.x + 5
        if self.current_mash_chars:
            cursor_x = self._draw_colored_chars(surface, self.current_mash_chars,
                                                 term_rect.x + 5, bottom_y, 1.0)
        # Blinking cursor
        if int(self.cursor_timer * 2) % 2 == 0:
            pygame.draw.rect(surface, BRIGHT_GREEN, (cursor_x, bottom_y, 8, 14))

        # Draw completed lines above the current line, from bottom up
        y = bottom_y - 16
        for i in range(len(self.player_lines) - 1, -1, -1):
            if y < term_rect.top:
                break
            line_chars = self.player_lines[i]
            age = max(0, min(1, self.player_line_timers[i] / 5.0))
            fade = max(0.3, age)
            self._draw_colored_chars(surface, line_chars, term_rect.x + 5, y, fade)
            y -= 16

        # Typing challenge display
        challenge_info = typing_challenge.get_display_info() if typing_challenge else None
        if challenge_info:
            self._draw_typing_challenge(surface, term_rect, challenge_info)

        surface.set_clip(clip)

    def _draw_typing_challenge(self, surface, term_rect, info):
        # Draw challenge box at bottom of terminal
        box_h = 50
        box_y = term_rect.bottom - box_h - 20
        box_rect = pygame.Rect(term_rect.x + 5, box_y,
                                term_rect.w - 10, box_h)
        # Background
        bg_surf = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        surface.blit(bg_surf, box_rect.topleft)

        # Border with action color
        pygame.draw.rect(surface, info['color'], box_rect, 2, border_radius=4)

        # Action label
        label_surf = self.small_font.render(f"[{info['label']}]", True, info['color'])
        surface.blit(label_surf, (box_rect.x + 5, box_rect.y + 3))

        # Timer bar
        timer_ratio = info['time_remaining'] / info['timeout']
        timer_w = int((box_rect.w - 10) * timer_ratio)
        timer_color = BRIGHT_GREEN if timer_ratio > 0.3 else RED
        pygame.draw.rect(surface, timer_color,
                         (box_rect.x + 5, box_rect.y + box_h - 6, timer_w, 3))

        # Command text with highlighting
        x = box_rect.x + 10
        y = box_rect.y + 20
        text = info['text']
        typed_idx = info['typed_index']
        flash_chars = info['flash_chars']

        for i, ch in enumerate(text):
            if i in flash_chars:
                color = flash_chars[i][0]
            elif i < typed_idx:
                color = BRIGHT_GREEN
            elif i == typed_idx:
                # Current char to type - highlighted
                color = (255, 255, 255)
                # Draw background highlight
                ch_surf = self.terminal_font.render(ch, True, color)
                pygame.draw.rect(surface, (0, 80, 40),
                                 (x - 1, y - 1, ch_surf.get_width() + 2, 18))
            else:
                color = DIM_GREEN
            ch_surf = self.terminal_font.render(ch, True, color)
            surface.blit(ch_surf, (x, y))
            x += ch_surf.get_width()

    def draw_enemy_terminal(self, surface, enemy):
        if not enemy:
            return

        clip = surface.get_clip()
        term_rect = pygame.Rect(self.enemy_panel.x + 5,
                                self.enemy_panel.y + self.terminal_start_y,
                                self.enemy_panel.w - 10,
                                self.enemy_panel.h - self.terminal_start_y - 5)
        surface.set_clip(term_rect)

        # Enemy terminal lines
        y = term_rect.bottom - 18
        lines = enemy.terminal_lines
        for i in range(len(lines) - 1, -1, -1):
            if y < term_rect.top:
                break
            text = lines[i]
            # Determine color based on content
            if "SEGFAULT" in text or "KERNEL PANIC" in text or "FATAL" in text:
                color = (255, 50, 50)
            elif "DDoS" in text or "DROP TABLE" in text or "PHISHING" in text or "ENCRYPTING" in text:
                color = (255, 150, 50)
            else:
                color = DIM_RED
            text_surf = self.mono_font.render(text[:80], True, color)
            surface.blit(text_surf, (term_rect.x + 5, y))
            y -= 16

        # Boot sequence current line (typing out)
        boot_line = enemy.get_boot_current_line()
        if boot_line is not None:
            boot_surf = self.mono_font.render(boot_line, True, RED)
            surface.blit(boot_surf, (term_rect.x + 5, term_rect.bottom - 18))

        # Telegraph warning: border pulse
        if enemy.is_telegraphing:
            t = pygame.time.get_ticks() / 100
            alpha = int(abs(math.sin(t)) * 150)
            warn_surf = pygame.Surface(term_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(warn_surf, (255, 0, 0, alpha), warn_surf.get_rect(), 3)
            surface.blit(warn_surf, term_rect.topleft)

        surface.set_clip(clip)

    def draw_bottom_bar(self, surface, game_state, wave_number, active_perks):
        pygame.draw.rect(surface, BOTTOM_BAR_BG, self.bottom_bar)
        pygame.draw.line(surface, (0, 60, 0),
                         (0, self.bottom_bar.y), (self.screen_w, self.bottom_bar.y))

        x = 15
        y = self.bottom_bar.y + 8

        # Wave number
        wave_surf = self.ui_font.render(f"WAVE {wave_number}", True, BRIGHT_GREEN)
        surface.blit(wave_surf, (x, y))
        x += wave_surf.get_width() + 30

        # LOC counter
        loc_surf = self.ui_font.render(f"LOC: {format_number(game_state.loc)}", True, GREEN)
        surface.blit(loc_surf, (x, y))
        x += loc_surf.get_width() + 30

        # Combo
        if game_state.combo >= 5:
            combo_color = self._get_combo_color(game_state.combo)
            combo_surf = self.ui_font.render(f"COMBO x{game_state.combo}", True, combo_color)
            surface.blit(combo_surf, (x, y))
            x += combo_surf.get_width() + 30

        # Active perks (show icons/names)
        if active_perks:
            perks_text = " | ".join(p['name'] for p in active_perks[:5])
            perks_surf = self.small_font.render(perks_text, True, CYAN)
            surface.blit(perks_surf, (x, y + 3))

    def draw_combo_display(self, surface, combo, is_epic):
        if combo < 5:
            return

        # Update bounce
        if combo != self.combo_last:
            self.combo_display_size = 1.3
            self.combo_last = combo

        self.combo_display_size = max(1.0, self.combo_display_size - 0.02)

        combo_color = self._get_combo_color(combo)
        text = f"x{combo}"
        rendered = self.combo_font.render(text, True, combo_color)

        if self.combo_display_size != 1.0:
            w = int(rendered.get_width() * self.combo_display_size)
            h = int(rendered.get_height() * self.combo_display_size)
            rendered = pygame.transform.scale(rendered, (w, h))

        x = self.screen_w // 2 - rendered.get_width() // 2
        y = 60
        surface.blit(rendered, (x, y))

        if is_epic:
            epic_text = "EPIC HACKING MODE"
            t = pygame.time.get_ticks() / 200
            pulse = int(abs(math.sin(t)) * 55 + 200)
            epic_color = (0, pulse, int(pulse * 0.4))
            epic_surf = self.big_font.render(epic_text, True, epic_color)
            x2 = self.screen_w // 2 - epic_surf.get_width() // 2
            surface.blit(epic_surf, (x2, y + 60))

    def _get_combo_color(self, combo):
        if combo >= 50:
            return GOLD
        elif combo >= 30:
            return (255, 100, 0)
        elif combo >= 15:
            return (255, 200, 0)
        else:
            return WHITE

    def draw_perk_choice(self, surface, perks, selected_index):
        # Dim background
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("CHOOSE A PERK", True, BRIGHT_GREEN)
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, 80))

        # Cards
        card_w = 280
        card_h = 200
        total_w = card_w * len(perks) + 30 * (len(perks) - 1)
        start_x = self.screen_w // 2 - total_w // 2
        card_y = 180

        card_rects = []
        for i, perk in enumerate(perks):
            x = start_x + i * (card_w + 30)
            rect = pygame.Rect(x, card_y, card_w, card_h)
            card_rects.append(rect)

            is_selected = i == selected_index
            bg_color = (20, 40, 30) if is_selected else (15, 20, 18)
            border_color = BRIGHT_GREEN if is_selected else DIM_GREEN

            # Card bg
            pygame.draw.rect(surface, bg_color, rect, border_radius=8)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)

            if is_selected:
                # Glow
                glow = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow, (0, 255, 100, 30), glow.get_rect(), 4, border_radius=10)
                surface.blit(glow, (x - 4, card_y - 4))

            # Perk name
            name_surf = self.perk_font.render(perk['name'], True, BRIGHT_GREEN)
            surface.blit(name_surf, (x + card_w // 2 - name_surf.get_width() // 2,
                                      card_y + 20))

            # Description (word wrap)
            self._draw_wrapped_text(surface, perk['description'], x + 15, card_y + 60,
                                     card_w - 30, self.small_font, GREEN)

            # Keybind hint
            key_text = f"[{i+1}]"
            key_surf = self.ui_font.render(key_text, True,
                                            BRIGHT_GREEN if is_selected else DIM_GREEN)
            surface.blit(key_surf, (x + card_w // 2 - key_surf.get_width() // 2,
                                     card_y + card_h - 35))

        return card_rects

    def draw_shop(self, surface, shop_items, game_state, selected_index):
        # Dim background
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("SHOP", True, BRIGHT_GREEN)
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, 40))

        # LOC display
        loc_text = f"LOC: {format_number(game_state.loc)}"
        loc_surf = self.big_font.render(loc_text, True, GREEN)
        surface.blit(loc_surf, (self.screen_w // 2 - loc_surf.get_width() // 2, 90))

        # Items as terminal ls output
        x = self.screen_w // 2 - 300
        y = 140
        item_rects = []

        for i, item in enumerate(shop_items):
            is_selected = i == selected_index
            can_afford = game_state.loc >= item['cost']
            purchased = item.get('purchased', False)

            rect = pygame.Rect(x - 5, y - 2, 610, 28)
            item_rects.append(rect)

            if is_selected:
                pygame.draw.rect(surface, (0, 40, 20), rect)

            prefix = ">" if is_selected else " "
            if purchased:
                status = "[INSTALLED]"
                color = DIM_GREEN
            elif can_afford:
                status = f"[{format_number(item['cost'])} LOC]"
                color = BRIGHT_GREEN
            else:
                status = f"[{format_number(item['cost'])} LOC]"
                color = (100, 100, 100)

            line = f"{prefix} {item['name']:<30} {item['description']:<25} {status}"
            text_surf = self.terminal_font.render(line, True, color)
            surface.blit(text_surf, (x, y))
            y += 28

        # Controls hint
        hint = self.small_font.render(
            "UP/DOWN: Navigate | ENTER: Buy | ESC: Continue to next wave", True, DIM_GREEN)
        surface.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, y + 20))

        return item_rects

    def draw_run_stats(self, surface, stats):
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render("RUN COMPLETE", True, GOLD)
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, 100))

        y = 200
        font = self.terminal_font
        for label, value in stats:
            text = f"  {label}: {value}"
            surf = font.render(text, True, GREEN)
            surface.blit(surf, (self.screen_w // 2 - 200, y))
            y += 28

        hint = self.ui_font.render("Press any key to continue", True, DIM_GREEN)
        surface.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, y + 40))

    def _draw_wrapped_text(self, surface, text, x, y, max_w, font, color):
        words = text.split()
        line = ""
        for word in words:
            test = line + word + " "
            if font.size(test)[0] > max_w:
                if line:
                    surf = font.render(line.strip(), True, color)
                    surface.blit(surf, (x, y))
                    y += 18
                line = word + " "
            else:
                line = test
        if line.strip():
            surf = font.render(line.strip(), True, color)
            surface.blit(surf, (x, y))
