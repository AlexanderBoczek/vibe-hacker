import random
import math
import pygame

# Colors
GREEN = (0, 220, 0)
BRIGHT_GREEN = (0, 255, 100)
DIM_GREEN = (0, 100, 60)
CYAN = (0, 200, 220)
GOLD = (255, 215, 0)
WHITE = (180, 180, 180)


class MatrixRain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 18)
        self.columns = width // 14
        self.drops = [random.randint(-30, 0) for _ in range(self.columns)]
        self.chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(){}[]<>/\\|;:=+-_"
        # Pre-render glyph cache
        self.glyph_cache = {}
        for ch in self.chars:
            for alpha in (60, 100, 160, 220):
                color = (0, alpha, 0)
                surf = self.font.render(ch, True, color)
                self.glyph_cache[(ch, alpha)] = surf
        self.intensity = 1.0  # scales with LOC/sec

    def update(self, dt, loc_per_sec):
        self.intensity = min(3.0, 1.0 + loc_per_sec / 50.0)
        speed = int(15 * self.intensity * dt * 60)
        for i in range(self.columns):
            self.drops[i] += max(1, speed)
            if self.drops[i] * 18 > self.height + random.randint(0, 200):
                self.drops[i] = random.randint(-20, 0)

    def draw(self, surface):
        for i in range(self.columns):
            if self.drops[i] < 0:
                continue
            x = i * 14
            y = self.drops[i] * 18
            ch = random.choice(self.chars)
            # Head of the drop is brighter
            alpha = 220
            if (ch, alpha) in self.glyph_cache:
                surface.blit(self.glyph_cache[(ch, alpha)], (x, y))
            # Trail
            for j in range(1, 6):
                ty = y - j * 18
                if ty < 0:
                    break
                trail_alpha = max(60, 220 - j * 40)
                tch = random.choice(self.chars)
                key = (tch, trail_alpha)
                if key in self.glyph_cache:
                    surface.blit(self.glyph_cache[key], (x, ty))


class Particle:
    def __init__(self, x, y, color=GREEN):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 200)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 50
        self.life = random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # gravity
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), size)


class FloatingText:
    def __init__(self, x, y, text, color=GREEN, size=24):
        self.x = x
        self.y = y
        self.start_y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.font = pygame.font.Font(None, size)
        self.rendered = self.font.render(text, True, color)

    def update(self, dt):
        self.life -= dt
        self.y = self.start_y - (1.0 - self.life) * 80
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(self.life * 255)))
        text_surf = self.rendered.copy()
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))


class EffectsManager:
    MAX_PARTICLES = 200
    MAX_FLOATING = 20

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.matrix_rain = MatrixRain(screen_width, screen_height)
        self.particles = []
        self.floating_texts = []
        self.screen_shake_trauma = 0.0
        self.crt_overlay = self._make_crt_overlay(screen_width, screen_height)
        self.combo_font = pygame.font.Font(None, 72)
        self.epic_font = pygame.font.Font(None, 48)

    def _make_crt_overlay(self, w, h):
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(overlay, (0, 0, 0, 30), (0, y), (w, y))
        return overlay

    def add_particles(self, x, y, count=10, color=GREEN):
        for _ in range(count):
            if len(self.particles) < self.MAX_PARTICLES:
                self.particles.append(Particle(x, y, color))

    def add_floating_text(self, x, y, text, amount=0):
        if len(self.floating_texts) >= self.MAX_FLOATING:
            self.floating_texts.pop(0)
        # Color and size based on amount
        if amount >= 1000:
            color = GOLD
            size = 36
        elif amount >= 100:
            color = CYAN
            size = 30
        else:
            color = BRIGHT_GREEN
            size = 24
        self.floating_texts.append(FloatingText(x, y, text, color, size))

    def add_trauma(self, amount):
        self.screen_shake_trauma = min(1.0, self.screen_shake_trauma + amount)

    def update(self, dt, loc_per_sec):
        self.matrix_rain.update(dt, loc_per_sec)
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]
        self.screen_shake_trauma = max(0, self.screen_shake_trauma - dt * 2)

    def get_shake_offset(self):
        if self.screen_shake_trauma <= 0:
            return 0, 0
        intensity = self.screen_shake_trauma ** 2 * 8
        ox = random.uniform(-intensity, intensity)
        oy = random.uniform(-intensity, intensity)
        return int(ox), int(oy)

    def draw_matrix_rain(self, surface):
        self.matrix_rain.draw(surface)

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

    def draw_floating_texts(self, surface):
        for ft in self.floating_texts:
            ft.draw(surface)

    def draw_crt_overlay(self, surface):
        surface.blit(self.crt_overlay, (0, 0))

    def draw_combo(self, surface, combo, is_epic):
        if combo < 5:
            return
        text = f"COMBO x{combo}"
        color = GOLD if is_epic else BRIGHT_GREEN
        rendered = self.combo_font.render(text, True, color)
        x = self.screen_width // 2 - rendered.get_width() // 2
        surface.blit(rendered, (x, 80))

        if is_epic:
            epic_text = "EPIC CODING MONTAGE"
            t = pygame.time.get_ticks() / 200
            pulse = int(abs(math.sin(t)) * 55 + 200)
            epic_color = (pulse, pulse, 0)
            rendered2 = self.epic_font.render(epic_text, True, epic_color)
            x2 = self.screen_width // 2 - rendered2.get_width() // 2
            surface.blit(rendered2, (x2, 140))
