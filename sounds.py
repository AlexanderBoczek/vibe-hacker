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
        self._generate_sounds()

    def _generate_sounds(self):
        # Pool of click variations
        for _ in range(8):
            freq = random.uniform(800, 1200)
            self.click_pool.append(self._make_tone(freq, 0.03, 0.3))

        # Wrong key click - lower pitch
        self.wrong_click = self._make_tone(400, 0.03, 0.2)

        # Achievement chime - two ascending tones
        tone1 = self._make_tone(600, 0.1, 0.3)
        tone2 = self._make_tone(900, 0.15, 0.3)
        # Combine them sequentially
        samples1 = self._get_samples(600, 0.1, 0.3)
        samples2 = self._get_samples(900, 0.15, 0.3)
        combined = array.array("h", samples1 + samples2)
        self.achievement_sound = pygame.mixer.Sound(buffer=combined)
        self.achievement_sound.set_volume(0.4)

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
        sound = pygame.mixer.Sound(buffer=samples)
        return sound

    def play_click(self):
        sound = random.choice(self.click_pool)
        sound.play()

    def play_wrong_click(self):
        self.wrong_click.play()

    def play_achievement(self):
        self.achievement_sound.play()
