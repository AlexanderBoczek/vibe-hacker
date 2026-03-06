import random
import math
import pygame


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size', 'gravity')

    def __init__(self, x, y, vx, vy, life, color, size, gravity=200):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), size)


class DamageNumber:
    def __init__(self, x, y, text, color, size=28):
        self.x = x
        self.y = y
        self.start_y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.font = pygame.font.Font(None, size)
        self.is_crit = size > 28

    def update(self, dt):
        self.life -= dt
        self.y = self.start_y - (1.0 - self.life) * 60
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(self.life * 255)))
        scale = 1.0
        if self.is_crit and self.life > 0.8:
            scale = 1.0 + (1.0 - (self.life - 0.8) / 0.2) * 0.5
        text_surf = self.font.render(self.text, True, self.color)
        if scale != 1.0:
            w = int(text_surf.get_width() * scale)
            h = int(text_surf.get_height() * scale)
            text_surf = pygame.transform.scale(text_surf, (w, h))
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x - text_surf.get_width() // 2), int(self.y)))


class MatrixRainColumn:
    __slots__ = ('x', 'y', 'speed', 'chars', 'length', 'color_base')

    def __init__(self, x, max_y, color_base):
        self.x = x
        self.y = random.randint(-400, 0)
        self.speed = random.uniform(80, 250)
        self.length = random.randint(5, 20)
        self.color_base = color_base
        self.chars = [chr(random.randint(0x30A0, 0x30FF)) if random.random() < 0.5
                      else str(random.randint(0, 9)) for _ in range(self.length)]

    def update(self, dt, speed_mult=1.0):
        self.y += self.speed * speed_mult * dt
        if random.random() < 0.05:
            idx = random.randint(0, self.length - 1)
            self.chars[idx] = chr(random.randint(0x30A0, 0x30FF)) if random.random() < 0.5 \
                else str(random.randint(0, 9))


class ParticleSystem:
    MAX_PARTICLES = 300
    MAX_DAMAGE_NUMBERS = 30

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.particles = []
        self.damage_numbers = []
        self.rain_font = pygame.font.Font(None, 18)

        # Matrix rain columns - green (left) and red (right)
        self.green_columns = []
        self.red_columns = []
        self._init_rain()

        # Rain glyph caches
        self.green_glyphs = {}
        self.red_glyphs = {}
        self._build_glyph_caches()

        # Combo fire particles
        self.fire_particles = []

        # Dust motes
        self.dust = []
        self._init_dust()

        self.rain_speed_mult = 1.0

    def _init_rain(self):
        mid = self.screen_w // 2
        col_spacing = 16
        for x in range(0, mid, col_spacing):
            self.green_columns.append(MatrixRainColumn(x, self.screen_h, (0, 1, 0)))
        for x in range(mid, self.screen_w, col_spacing):
            self.red_columns.append(MatrixRainColumn(x, self.screen_h, (1, 0, 0)))

    def _build_glyph_caches(self):
        chars = [chr(c) for c in range(0x30A0, 0x30FF)] + [str(i) for i in range(10)]
        for ch in chars:
            for alpha_val in (40, 80, 120, 180, 220):
                g_color = (0, alpha_val, 0)
                r_color = (alpha_val, 0, 0)
                self.green_glyphs[(ch, alpha_val)] = self.rain_font.render(ch, True, g_color)
                self.red_glyphs[(ch, alpha_val)] = self.rain_font.render(ch, True, r_color)

    def _init_dust(self):
        for _ in range(20):
            self.dust.append({
                'x': random.uniform(0, self.screen_w),
                'y': random.uniform(0, self.screen_h),
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-3, 3),
                'alpha': random.uniform(0.1, 0.4),
                'size': random.randint(1, 2),
            })

    def resize(self, w, h):
        self.screen_w = w
        self.screen_h = h
        self.green_columns.clear()
        self.red_columns.clear()
        self._init_rain()
        self.dust.clear()
        self._init_dust()

    def update(self, dt, combo=0, is_combat=True):
        self.rain_speed_mult = 1.5 if is_combat else 0.5

        # Matrix rain
        mid = self.screen_w // 2
        for col in self.green_columns:
            col.update(dt, self.rain_speed_mult)
            if col.y - col.length * 18 > self.screen_h:
                col.y = random.randint(-300, -50)
                col.speed = random.uniform(80, 250)
        for col in self.red_columns:
            col.update(dt, self.rain_speed_mult)
            if col.y - col.length * 18 > self.screen_h:
                col.y = random.randint(-300, -50)
                col.speed = random.uniform(80, 250)

        # Particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Damage numbers
        self.damage_numbers = [d for d in self.damage_numbers if d.update(dt)]

        # Combo fire
        if combo >= 15:
            intensity = min(10, (combo - 15) // 5 + 1)
            for _ in range(intensity):
                if len(self.fire_particles) < 100:
                    # Fire from bottom of left panel
                    x = random.uniform(10, mid - 10)
                    y = self.screen_h - 60
                    vx = random.uniform(-20, 20)
                    vy = random.uniform(-100, -40)
                    life = random.uniform(0.3, 0.8)
                    if combo >= 50:
                        color = (0, 255, random.randint(50, 150))
                    else:
                        color = (255, random.randint(100, 200), 0)
                    self.fire_particles.append(
                        Particle(x, y, vx, vy, life, color, random.randint(2, 5), gravity=-50)
                    )
        self.fire_particles = [p for p in self.fire_particles if p.update(dt)]

        # Dust
        for d in self.dust:
            d['x'] += d['vx'] * dt
            d['y'] += d['vy'] * dt
            if d['x'] < 0 or d['x'] > self.screen_w:
                d['vx'] *= -1
            if d['y'] < 0 or d['y'] > self.screen_h:
                d['vy'] *= -1

    def add_particles(self, x, y, count=10, color=(0, 255, 0)):
        for _ in range(count):
            if len(self.particles) >= self.MAX_PARTICLES:
                break
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            life = random.uniform(0.3, 0.8)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, vx, vy, life, color, size))

    def add_damage_number(self, x, y, amount, is_player_damage=False, is_crit=False):
        if is_player_damage:
            color = (255, 60, 60)
            text = f"-{int(amount)}"
        else:
            color = (0, 255, 100)
            text = f"{int(amount)}"
        size = 36 if is_crit else 28
        if len(self.damage_numbers) >= self.MAX_DAMAGE_NUMBERS:
            self.damage_numbers.pop(0)
        self.damage_numbers.append(DamageNumber(x, y, text, color, size))

    def draw_matrix_rain(self, surface):
        for col in self.green_columns:
            self._draw_rain_column(surface, col, self.green_glyphs)
        for col in self.red_columns:
            self._draw_rain_column(surface, col, self.red_glyphs)

    def _draw_rain_column(self, surface, col, glyph_cache):
        for i, ch in enumerate(col.chars):
            y = int(col.y) - i * 18
            if y < -18 or y > self.screen_h:
                continue
            if i == 0:
                alpha_val = 220
            elif i < 3:
                alpha_val = 180
            elif i < 6:
                alpha_val = 120
            elif i < 10:
                alpha_val = 80
            else:
                alpha_val = 40
            key = (ch, alpha_val)
            if key in glyph_cache:
                surface.blit(glyph_cache[key], (col.x, y))

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)
        for p in self.fire_particles:
            p.draw(surface)

    def draw_damage_numbers(self, surface):
        for d in self.damage_numbers:
            d.draw(surface)

    def draw_dust(self, surface):
        for d in self.dust:
            alpha = int(d['alpha'] * 255)
            color = (alpha, alpha, alpha)
            pygame.draw.circle(surface, color, (int(d['x']), int(d['y'])), d['size'])
