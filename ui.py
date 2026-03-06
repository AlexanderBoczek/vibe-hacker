import pygame
import math
from code_generator import (
    TOKEN_KEYWORD, TOKEN_STRING, TOKEN_COMMENT,
    TOKEN_NUMBER, TOKEN_OPERATOR, TOKEN_DEFAULT,
)
import upgrades as upgrades_module

# Colors
BG_COLOR = (10, 10, 15)
EDITOR_BG = (15, 20, 25)
SHOP_BG = (20, 15, 25)
TOP_BAR_BG = (5, 5, 10)
STATUS_BAR_BG = (5, 5, 10)
LINE_NUM_COLOR = (0, 80, 0)
CURSOR_COLOR = (0, 255, 100)
HINT_BG = (0, 80, 40)
SEPARATOR_COLOR = (0, 60, 0)
TAB_ACTIVE_BG = (40, 30, 50)
TAB_INACTIVE_BG = (20, 15, 25)
AFFORDABLE_COLOR = (0, 255, 100)
UNAFFORDABLE_COLOR = (120, 120, 120)
MAXED_COLOR = (100, 100, 0)

TOKEN_COLORS = {
    TOKEN_KEYWORD: (0, 255, 100),
    TOKEN_STRING: (0, 200, 220),
    TOKEN_COMMENT: (0, 100, 60),
    TOKEN_NUMBER: (200, 200, 0),
    TOKEN_OPERATOR: (180, 180, 180),
    TOKEN_DEFAULT: (0, 220, 0),
}

# Layout
SCREEN_W = 1920
SCREEN_H = 1080
TOP_BAR_H = 45
STATUS_BAR_H = 30
EDITOR_W = int(SCREEN_W * 0.6)
SHOP_W = SCREEN_W - EDITOR_W
CONTENT_TOP = TOP_BAR_H
CONTENT_BOTTOM = SCREEN_H - STATUS_BAR_H
CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP

MAX_EDITOR_LINES = 200


def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return f"{int(n)}"


class CodeEditor:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.line_height = 20
        self.lines = []  # list of [(char, token_type), ...]
        self.current_line = []
        self.line_number = 1
        self.scroll_offset = 0
        self.cursor_blink = 0.0
        self.x = 0
        self.y = CONTENT_TOP
        self.w = EDITOR_W
        self.h = CONTENT_H
        self.line_num_width = 50
        self.code_x = self.line_num_width + 10

    def add_chars(self, chars_with_tokens):
        """Add typed characters to the editor display."""
        for ch, token_type in chars_with_tokens:
            self.current_line.append((ch, token_type))

    def complete_line(self):
        """Finish current line and start a new one."""
        self.lines.append(list(self.current_line))
        self.current_line = []
        self.line_number += 1
        if len(self.lines) > MAX_EDITOR_LINES:
            self.lines = self.lines[-MAX_EDITOR_LINES:]

    def update(self, dt):
        self.cursor_blink += dt
        # Auto-scroll to keep current line visible
        visible_lines = self.h // self.line_height - 1
        total = len(self.lines) + 1  # +1 for current line
        if total > visible_lines:
            self.scroll_offset = total - visible_lines

    def draw(self, surface, code_gen):
        # Editor background
        editor_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, EDITOR_BG, editor_rect)
        pygame.draw.line(surface, SEPARATOR_COLOR,
                         (self.w, self.y), (self.w, self.y + self.h))

        # Clip to editor area
        clip = surface.get_clip()
        surface.set_clip(editor_rect)

        visible_lines = self.h // self.line_height
        start = self.scroll_offset
        y = self.y + 5

        # Draw completed lines
        for i in range(start, len(self.lines)):
            if y > self.y + self.h:
                break
            line_idx = i + 1
            # Line number
            ln_surf = self.font.render(f"{line_idx:>4}", True, LINE_NUM_COLOR)
            surface.blit(ln_surf, (self.x + 5, y))
            # Code
            x = self.x + self.code_x
            for ch, token_type in self.lines[i]:
                color = TOKEN_COLORS.get(token_type, TOKEN_COLORS[TOKEN_DEFAULT])
                ch_surf = self.font.render(ch, True, color)
                surface.blit(ch_surf, (x, y))
                x += ch_surf.get_width()
            y += self.line_height

        # Draw current line
        if y <= self.y + self.h:
            ln_surf = self.font.render(f"{self.line_number:>4}", True, LINE_NUM_COLOR)
            surface.blit(ln_surf, (self.x + 5, y))
            x = self.x + self.code_x
            for ch, token_type in self.current_line:
                color = TOKEN_COLORS.get(token_type, TOKEN_COLORS[TOKEN_DEFAULT])
                ch_surf = self.font.render(ch, True, color)
                surface.blit(ch_surf, (x, y))
                x += ch_surf.get_width()

            # Draw next-char hint and cursor
            next_ch, next_token = code_gen.get_next_char()
            if next_ch is not None:
                # Hint background
                hint_surf = self.font.render(next_ch, True, (0, 180, 80))
                hw = hint_surf.get_width()
                pygame.draw.rect(surface, HINT_BG, (x, y, hw + 2, self.line_height))
                surface.blit(hint_surf, (x + 1, y))

            # Blinking cursor
            if int(self.cursor_blink * 2) % 2 == 0:
                pygame.draw.rect(surface, CURSOR_COLOR, (x, y, 2, self.line_height))

        surface.set_clip(clip)

    def get_cursor_screen_pos(self):
        """Get approximate screen position of cursor for effects."""
        visible_lines = len(self.lines) + 1 - self.scroll_offset
        y = self.y + 5 + visible_lines * self.line_height
        x = self.x + self.code_x + len(self.current_line) * 9
        return x, y


class ShopPanel:
    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 28)
        self.tab_font = pygame.font.Font(None, 20)
        self.x = EDITOR_W
        self.y = CONTENT_TOP
        self.w = SHOP_W
        self.h = CONTENT_H
        self.active_tab = 0  # index into CATEGORY_ORDER
        self.scroll_offset = 0
        self.item_rects = []  # for click detection: (rect, upgrade)
        self.tab_rects = []

    def handle_click(self, pos, game_state):
        """Handle mouse click in shop. Returns upgrade if purchased."""
        # Check tabs
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(pos):
                self.active_tab = i
                self.scroll_offset = 0
                return None

        # Check items
        for rect, upg in self.item_rects:
            if rect.collidepoint(pos):
                count = game_state.owned_upgrades.get(upg.id, 0)
                cost = upg.get_cost(count)
                if upg.can_buy(count) and game_state.loc >= cost:
                    game_state.spend_loc(cost)
                    game_state.owned_upgrades[upg.id] = count + 1
                    return upg
        return None

    def handle_scroll(self, direction):
        self.scroll_offset = max(0, self.scroll_offset + direction * 40)

    def draw(self, surface, game_state):
        # Background
        shop_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, SHOP_BG, shop_rect)

        clip = surface.get_clip()
        surface.set_clip(shop_rect)

        self.item_rects = []
        self.tab_rects = []

        # Tabs
        tab_y = self.y + 5
        tab_x = self.x + 10
        tab_w = (self.w - 20) // len(upgrades_module.CATEGORY_ORDER)
        for i, cat_key in enumerate(upgrades_module.CATEGORY_ORDER):
            cat_name = upgrades_module.CATEGORY_NAMES[cat_key]
            bg = TAB_ACTIVE_BG if i == self.active_tab else TAB_INACTIVE_BG
            rect = pygame.Rect(tab_x + i * tab_w, tab_y, tab_w - 4, 28)
            pygame.draw.rect(surface, bg, rect, border_radius=4)
            text = self.tab_font.render(cat_name, True, (0, 200, 100))
            surface.blit(text, (rect.x + rect.w // 2 - text.get_width() // 2,
                                rect.y + 6))
            self.tab_rects.append(rect)

        # Items
        active_cat = upgrades_module.CATEGORY_ORDER[self.active_tab]
        visible_upgrades = [
            u for u in upgrades_module.UPGRADES
            if u.category == active_cat and u.is_unlocked(game_state.total_loc)
        ]

        item_y = tab_y + 40 - self.scroll_offset
        for upg in visible_upgrades:
            if item_y > self.y + self.h:
                break
            if item_y + 70 > self.y:
                count = game_state.owned_upgrades.get(upg.id, 0)
                cost = upg.get_cost(count)
                can_afford = game_state.loc >= cost
                is_maxed = not upg.can_buy(count)

                # Item box
                item_rect = pygame.Rect(self.x + 10, item_y, self.w - 20, 65)
                border_color = MAXED_COLOR if is_maxed else (
                    AFFORDABLE_COLOR if can_afford else UNAFFORDABLE_COLOR)
                pygame.draw.rect(surface, (25, 20, 30), item_rect, border_radius=4)
                pygame.draw.rect(surface, border_color, item_rect, 1, border_radius=4)

                # Name + count
                name_text = upg.name
                if upg.max_count == -1:
                    name_text += f" ({count})"
                name_surf = self.title_font.render(name_text, True, border_color)
                surface.blit(name_surf, (item_rect.x + 8, item_rect.y + 5))

                # Description
                desc_surf = self.font.render(upg.description, True, (0, 160, 80))
                surface.blit(desc_surf, (item_rect.x + 8, item_rect.y + 27))

                # Cost
                if is_maxed:
                    cost_text = "MAXED"
                else:
                    cost_text = f"Cost: {format_number(cost)} LOC"
                cost_color = AFFORDABLE_COLOR if can_afford else UNAFFORDABLE_COLOR
                if is_maxed:
                    cost_color = MAXED_COLOR
                cost_surf = self.font.render(cost_text, True, cost_color)
                surface.blit(cost_surf, (item_rect.x + 8, item_rect.y + 46))

                if not is_maxed:
                    self.item_rects.append((item_rect, upg))

            item_y += 72

        surface.set_clip(clip)


class TopBar:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.display_loc = 0.0  # animated lerp

    def update(self, dt, actual_loc):
        # Lerp toward actual value
        diff = actual_loc - self.display_loc
        self.display_loc += diff * min(1.0, dt * 10)

    def draw(self, surface, game_state, loc_per_sec, global_mult):
        bar_rect = pygame.Rect(0, 0, SCREEN_W, TOP_BAR_H)
        pygame.draw.rect(surface, TOP_BAR_BG, bar_rect)
        pygame.draw.line(surface, SEPARATOR_COLOR, (0, TOP_BAR_H), (SCREEN_W, TOP_BAR_H))

        # LOC counter
        loc_text = f"LOC: {format_number(self.display_loc)}"
        loc_surf = self.font.render(loc_text, True, (0, 255, 100))
        surface.blit(loc_surf, (20, 8))

        # LOC/sec
        rate_text = f"{format_number(loc_per_sec)} LOC/sec"
        rate_surf = self.small_font.render(rate_text, True, (0, 180, 80))
        surface.blit(rate_surf, (300, 14))

        # Total LOC
        total_text = f"Total: {format_number(game_state.total_loc)}"
        total_surf = self.small_font.render(total_text, True, (0, 140, 60))
        surface.blit(total_surf, (550, 14))

        # Multiplier
        if global_mult > 1:
            mult_text = f"x{format_number(global_mult)} mult"
            mult_surf = self.small_font.render(mult_text, True, (200, 200, 0))
            surface.blit(mult_surf, (750, 14))


class StatusBar:
    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.messages = [
            "Press any key to start coding...",
            "The vibes are immaculate",
            "Ship it!",
            "git commit -m 'it works trust me'",
            "Debugging is just reading your own code",
            "It's not a bug, it's a feature",
            "Works on my machine!",
            "Have you tried turning it off and on again?",
        ]
        self.current_message = self.messages[0]
        self.message_timer = 0.0
        self.message_duration = 5.0
        self.milestone_queue = []
        self.milestone_timer = 0.0

    def push_milestone(self, message):
        self.milestone_queue.append(message)

    def update(self, dt):
        if self.milestone_timer > 0:
            self.milestone_timer -= dt
            if self.milestone_timer <= 0 and self.milestone_queue:
                msg = self.milestone_queue.pop(0)
                self.current_message = f"*** {msg} ***"
                self.milestone_timer = 4.0
            return

        if self.milestone_queue:
            msg = self.milestone_queue.pop(0)
            self.current_message = f"*** {msg} ***"
            self.milestone_timer = 4.0
            return

        self.message_timer += dt
        if self.message_timer >= self.message_duration:
            self.message_timer = 0.0
            import random
            self.current_message = random.choice(self.messages)

    def draw(self, surface):
        bar_rect = pygame.Rect(0, SCREEN_H - STATUS_BAR_H, SCREEN_W, STATUS_BAR_H)
        pygame.draw.rect(surface, STATUS_BAR_BG, bar_rect)
        pygame.draw.line(surface, SEPARATOR_COLOR,
                         (0, SCREEN_H - STATUS_BAR_H), (SCREEN_W, SCREEN_H - STATUS_BAR_H))
        text_surf = self.font.render(self.current_message, True, (0, 180, 80))
        surface.blit(text_surf, (20, SCREEN_H - STATUS_BAR_H + 6))
