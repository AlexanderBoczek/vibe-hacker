import random
import time
from commands import get_random_command, ACTION_LABELS, ACTION_COLORS


class TypingChallenge:
    def __init__(self):
        self.active = False
        self.action_type = None
        self.command_text = ""
        self.typed_index = 0
        self.label = ""
        self.color = (0, 255, 0)
        self.spawn_timer = -5.0  # initial delay before first challenge
        self.spawn_interval = 6.0
        self.timeout = 15.0
        self.time_remaining = 0.0
        self.flash_chars = {}  # index -> (color, timer)

    def update(self, dt, wave_number=1):
        # Update char flashes
        to_remove = []
        for idx, (color, timer) in self.flash_chars.items():
            new_timer = timer - dt
            if new_timer <= 0:
                to_remove.append(idx)
            else:
                self.flash_chars[idx] = (color, new_timer)
        for idx in to_remove:
            del self.flash_chars[idx]

        if self.active:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.fail()
                return "timeout"
            return None

        self.spawn_timer += dt
        interval = max(3.0, self.spawn_interval - wave_number * 0.3)
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self._spawn_challenge()
        return None

    def _spawn_challenge(self):
        self.action_type, self.command_text = get_random_command()
        self.typed_index = 0
        self.label = ACTION_LABELS[self.action_type]
        self.color = ACTION_COLORS[self.action_type]
        self.active = True
        self.time_remaining = self.timeout
        self.flash_chars = {}

    def type_char(self, char):
        if not self.active:
            return None

        expected = self.command_text[self.typed_index]
        if char == expected:
            self.flash_chars[self.typed_index] = ((0, 255, 100), 0.15)
            self.typed_index += 1
            if self.typed_index >= len(self.command_text):
                result = {
                    "action": self.action_type,
                    "command": self.command_text,
                    "label": self.label,
                    "color": self.color,
                }
                self.active = False
                self.spawn_timer = 0
                return result
            return "correct"
        else:
            self.flash_chars[self.typed_index] = ((255, 50, 50), 0.2)
            return "wrong"

    def fail(self):
        self.active = False
        self.spawn_timer = 0

    def get_display_info(self):
        if not self.active:
            return None
        return {
            "label": self.label,
            "color": self.color,
            "text": self.command_text,
            "typed_index": self.typed_index,
            "time_remaining": self.time_remaining,
            "timeout": self.timeout,
            "flash_chars": self.flash_chars,
        }
