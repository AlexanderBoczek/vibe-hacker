import pygame
import sys
import upgrades as upgrades_module
from game_state import GameState
from code_generator import CodeGenerator
from effects import EffectsManager
from ui import CodeEditor, ShopPanel, TopBar, StatusBar, SCREEN_W, SCREEN_H, format_number
from sounds import SoundManager

FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Vibe Hacker")
    clock = pygame.time.Clock()

    # Initialize systems
    game_state = GameState()
    game_state.load()
    code_gen = CodeGenerator()
    effects = EffectsManager(SCREEN_W, SCREEN_H)
    editor = CodeEditor()
    shop = ShopPanel()
    top_bar = TopBar()
    status_bar = StatusBar()
    sound_mgr = SoundManager()

    # Render surface for shake offset
    render_surface = pygame.Surface((SCREEN_W, SCREEN_H))

    # Auto-typer timing
    auto_type_timer = 0.0
    auto_type_interval = 0.1  # generate auto code every 100ms

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)  # cap delta

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.save()
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state.save()
                    running = False
                    continue

                # Ignore modifier-only keys and non-printable
                if event.unicode and event.unicode.isprintable():
                    handle_keypress(event.unicode, game_state, code_gen,
                                    editor, effects, sound_mgr)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    purchased = shop.handle_click(event.pos, game_state)
                    if purchased:
                        sound_mgr.play_achievement()
                elif event.button == 4:  # scroll up
                    shop.handle_scroll(-1)
                elif event.button == 5:  # scroll down
                    shop.handle_scroll(1)

            if event.type == pygame.MOUSEWHEEL:
                shop.handle_scroll(-event.y)

        # --- Update ---
        game_state.update(dt)

        # Calculate rates
        global_mult = game_state.get_global_multiplier(upgrades_module)
        auto_loc_sec = game_state.get_auto_loc_per_sec(upgrades_module) * global_mult
        game_state.loc_per_sec = auto_loc_sec

        # Auto-typers: generate passive LOC and visible code
        if auto_loc_sec > 0:
            auto_type_timer += dt
            if auto_type_timer >= auto_type_interval:
                auto_type_timer -= auto_type_interval
                loc_this_tick = auto_loc_sec * auto_type_interval
                game_state.add_loc(loc_this_tick)

                # Generate visible characters proportional to LOC
                chars_to_show = max(1, int(loc_this_tick * 2))
                chars_to_show = min(chars_to_show, 50)  # cap visual chars
                for _ in range(chars_to_show):
                    chars, lines_done = code_gen.advance(1)
                    if chars:
                        editor.add_chars(chars)
                    for _ in range(lines_done):
                        editor.complete_line()

        # Milestones
        while game_state.pending_milestones:
            msg = game_state.pending_milestones.pop(0)
            status_bar.push_milestone(msg)
            sound_mgr.play_achievement()

        editor.update(dt)
        effects.update(dt, auto_loc_sec)
        top_bar.update(dt, game_state.loc)
        status_bar.update(dt)

        # --- Render ---
        render_surface.fill((0, 0, 0))

        # Layer 1: Matrix rain
        effects.draw_matrix_rain(render_surface)

        # Layer 2: Code editor
        editor.draw(render_surface, code_gen)

        # Layer 3: Shop panel
        shop.draw(render_surface, game_state)

        # Layer 4: Top bar
        top_bar.draw(render_surface, game_state, auto_loc_sec, global_mult)

        # Layer 5: Status bar
        status_bar.draw(render_surface)

        # Layer 6: Floating text
        effects.draw_floating_texts(render_surface)

        # Layer 7: Particles
        effects.draw_particles(render_surface)

        # Layer 8: Combo display
        effects.draw_combo(render_surface, game_state.combo, game_state.is_epic_mode())

        # Layer 9: CRT overlay
        effects.draw_crt_overlay(render_surface)

        # Apply screen shake
        ox, oy = effects.get_shake_offset()
        screen.fill((0, 0, 0))
        screen.blit(render_surface, (ox, oy))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def handle_keypress(char, game_state, code_gen, editor, effects, sound_mgr):
    """Handle a printable keypress."""
    expected_char, _ = code_gen.get_next_char()

    correct = (expected_char is not None and char == expected_char)

    if correct:
        game_state.register_correct_key()
        sound_mgr.play_click()
        # Correct key: get full chars per press bonus
        chars_per_press = game_state.get_chars_per_press(upgrades_module)
    else:
        game_state.register_wrong_key()
        sound_mgr.play_wrong_click()
        # Wrong key: only 1 character, no bonus
        chars_per_press = 1

    # Advance code generator
    chars, lines_completed = code_gen.advance(chars_per_press)
    if chars:
        editor.add_chars(chars)

    if lines_completed > 0:
        combo_mult = game_state.get_combo_multiplier()
        global_mult = game_state.get_global_multiplier(upgrades_module)
        loc_earned = lines_completed * combo_mult * global_mult
        game_state.add_loc(loc_earned)

        for _ in range(lines_completed):
            editor.complete_line()

        # Effects
        cx, cy = editor.get_cursor_screen_pos()
        effects.add_floating_text(cx, cy - 20,
                                  f"+{format_number(loc_earned)} LOC",
                                  amount=loc_earned)
        effects.add_particles(cx, cy, count=15)
        effects.add_trauma(0.1 + min(0.3, game_state.combo * 0.005))


if __name__ == "__main__":
    main()
