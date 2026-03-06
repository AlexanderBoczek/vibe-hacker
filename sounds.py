import array
import math
import random

import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        self.click_pool = []
        self.wrong_click = None
        self.achievement_sound = None
        self.attack_sound = None
        self.defend_sound = None
        self.hack_sound = None
        self.damage_sound = None
        self.crit_sound = None
        self.wave_clear_sound = None
        self.death_sound = None
        self._generate_sounds()

    def _generate_sounds(self):
        # Click variations
        for _ in range(8):
            freq = random.uniform(800, 1200)
            self.click_pool.append(self._make_tone(freq, 0.03, 0.3))

        self.wrong_click = self._make_tone(400, 0.03, 0.2)

        # Achievement chime
        samples1 = self._get_samples(600, 0.1, 0.3)
        samples2 = self._get_samples(900, 0.15, 0.3)
        combined = array.array("h", samples1 + samples2)
        self.achievement_sound = pygame.mixer.Sound(buffer=combined)
        self.achievement_sound.set_volume(0.4)

        # Attack - sharp rising tone
        self.attack_sound = self._make_sweep(400, 1200, 0.1, 0.4)

        # Defend - low hum
        self.defend_sound = self._make_tone(300, 0.15, 0.3)

        # Hack - descending tone
        self.hack_sound = self._make_sweep(1000, 400, 0.12, 0.35)

        # Damage taken - low thud
        self.damage_sound = self._make_noise(0.08, 0.4)

        # Critical hit - sharp crack
        s1 = self._get_samples(1500, 0.02, 0.5)
        s2 = self._get_samples(800, 0.05, 0.4)
        self.crit_sound = pygame.mixer.Sound(buffer=array.array("h", s1 + s2))

        # Wave clear - ascending chord
        s1 = self._get_samples(400, 0.15, 0.3)
        s2 = self._get_samples(500, 0.15, 0.3)
        s3 = self._get_samples(600, 0.15, 0.3)
        s4 = self._get_samples(800, 0.2, 0.35)
        combined = array.array("h")
        for i in range(len(s1)):
            val = s1[i] // 3
            if i < len(s2):
                val += s2[i] // 3
            if i < len(s3):
                val += s3[i] // 3
            combined.append(max(-32767, min(32767, val)))
        combined.extend(s4)
        self.wave_clear_sound = pygame.mixer.Sound(buffer=combined)
        self.wave_clear_sound.set_volume(0.5)

        # Death - descending rumble
        self.death_sound = self._make_sweep(600, 100, 0.3, 0.5)

    def _get_samples(self, freq, duration, volume):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        samples = array.array("h")
        for i in range(n_samples):
            t = i / sample_rate
            envelope = max(0, 1.0 - t / duration)
            val = volume * envelope * math.sin(2 * math.pi * freq * t)
            samples.append(int(val * 32767))
        return samples

    def _make_tone(self, freq, duration, volume):
        samples = self._get_samples(freq, duration, volume)
        return pygame.mixer.Sound(buffer=samples)

    def _make_sweep(self, freq_start, freq_end, duration, volume):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        samples = array.array("h")
        for i in range(n_samples):
            t = i / sample_rate
            progress = t / duration
            freq = freq_start + (freq_end - freq_start) * progress
            envelope = max(0, 1.0 - progress)
            val = volume * envelope * math.sin(2 * math.pi * freq * t)
            samples.append(int(val * 32767))
        return pygame.mixer.Sound(buffer=samples)

    def _make_noise(self, duration, volume):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        samples = array.array("h")
        for i in range(n_samples):
            t = i / sample_rate
            envelope = max(0, 1.0 - t / duration)
            val = volume * envelope * random.uniform(-1, 1)
            # Low pass by averaging
            samples.append(int(val * 32767))
        return pygame.mixer.Sound(buffer=samples)

    def play_click(self):
        random.choice(self.click_pool).play()

    def play_wrong_click(self):
        self.wrong_click.play()

    def play_achievement(self):
        self.achievement_sound.play()

    def play_attack(self):
        self.attack_sound.play()

    def play_defend(self):
        self.defend_sound.play()

    def play_hack(self):
        self.hack_sound.play()

    def play_damage(self):
        self.damage_sound.play()

    def play_crit(self):
        self.crit_sound.play()

    def play_wave_clear(self):
        self.wave_clear_sound.play()

    def play_death(self):
        self.death_sound.play()
