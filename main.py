import pygame
import sys
import random

from game_state import GameState, TOTAL_WAVES
from effects import ScreenEffects
from particles import ParticleSystem
from renderer import Renderer, SCREEN_W, SCREEN_H
from sounds import SoundManager
from typing_challenge import TypingChallenge
from battle import BattleSystem
from upgrades import get_perk_choices, get_shop_items, RELICS

FPS = 60

# Game states
STATE_BATTLE = "battle"
STATE_PERK_CHOICE = "perk_choice"
STATE_SHOP = "shop"
STATE_DEATH = "death"
STATE_RUN_COMPLETE = "run_complete"


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Hacker Battle")
    clock = pygame.time.Clock()

    # Core systems
    game_state = GameState()
    game_state.load()
    game_state.start_new_run()

    sound_mgr = SoundManager()
    effects = ScreenEffects(SCREEN_W, SCREEN_H)
    particles = ParticleSystem(SCREEN_W, SCREEN_H)
    renderer = Renderer(SCREEN_W, SCREEN_H)
    typing_challenge = TypingChallenge()
    battle = BattleSystem(game_state, effects, particles, renderer, sound_mgr)

    current_w, current_h = screen.get_size()
    if (current_w, current_h) != (SCREEN_W, SCREEN_H):
        _handle_resize(current_w, current_h, effects, particles, renderer)

    render_surface = pygame.Surface((current_w, current_h))

    # State
    state = STATE_BATTLE
    battle.start_wave(game_state.wave)

    # Perk choice state
    perk_choices = []
    perk_selected = 0

    # Shop state
    shop_items = []
    shop_selected = 0

    # Run stats
    run_stats = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.save()
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                render_surface = pygame.Surface((current_w, current_h))
                _handle_resize(current_w, current_h, effects, particles, renderer)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_SHOP:
                        # Leave shop, start next wave
                        game_state.wave += 1
                        battle.start_wave(game_state.wave)
                        typing_challenge = TypingChallenge()
                        state = STATE_BATTLE
                    elif state == STATE_BATTLE:
                        game_state.save()
                        running = False
                    continue

                if state == STATE_BATTLE:
                    _handle_battle_key(event, game_state, typing_challenge,
                                       battle, renderer, effects, sound_mgr)

                elif state == STATE_PERK_CHOICE:
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        idx = event.key - pygame.K_1
                        if idx < len(perk_choices):
                            perk_selected = idx
                            game_state.add_perk(perk_choices[idx])
                            renderer.add_player_line(
                                f"  [PERK] {perk_choices[idx]['name']} acquired!",
                                (0, 200, 220))
                            sound_mgr.play_achievement()
                            # Move to shop
                            shop_items = get_shop_items(game_state, game_state.wave)
                            shop_selected = 0
                            state = STATE_SHOP

                    elif event.key == pygame.K_LEFT:
                        perk_selected = max(0, perk_selected - 1)
                    elif event.key == pygame.K_RIGHT:
                        perk_selected = min(len(perk_choices) - 1, perk_selected + 1)
                    elif event.key == pygame.K_RETURN:
                        if perk_choices:
                            idx = perk_selected
                            game_state.add_perk(perk_choices[idx])
                            renderer.add_player_line(
                                f"  [PERK] {perk_choices[idx]['name']} acquired!",
                                (0, 200, 220))
                            sound_mgr.play_achievement()
                            shop_items = get_shop_items(game_state, game_state.wave)
                            shop_selected = 0
                            state = STATE_SHOP

                elif state == STATE_SHOP:
                    if event.key == pygame.K_UP:
                        shop_selected = max(0, shop_selected - 1)
                    elif event.key == pygame.K_DOWN:
                        shop_selected = min(len(shop_items) - 1, shop_selected + 1)
                    elif event.key == pygame.K_RETURN:
                        if shop_items and shop_selected < len(shop_items):
                            item = shop_items[shop_selected]
                            if not item.get('purchased') and game_state.spend_loc(item['cost']):
                                _apply_shop_item(item, game_state)
                                item['purchased'] = True
                                sound_mgr.play_achievement()
                                # Refresh items
                                shop_items = get_shop_items(game_state, game_state.wave)
                                # Mark already purchased
                                shop_selected = min(shop_selected, len(shop_items) - 1)

                elif state == STATE_DEATH:
                    if effects.death_timer > 4.0 and effects.game_over_char_idx >= len(effects.game_over_text):
                        # Restart
                        game_state.start_new_run()
                        effects.death_active = False
                        typing_challenge = TypingChallenge()
                        battle = BattleSystem(game_state, effects, particles, renderer, sound_mgr)
                        battle.start_wave(1)
                        state = STATE_BATTLE

                elif state == STATE_RUN_COMPLETE:
                    # Any key to restart
                    game_state.start_new_run()
                    typing_challenge = TypingChallenge()
                    battle = BattleSystem(game_state, effects, particles, renderer, sound_mgr)
                    battle.start_wave(1)
                    state = STATE_BATTLE

        if not running:
            break

        # --- Update ---
        frozen = effects.update(dt)
        if not frozen:
            game_state.update(dt)
            particles.update(dt, game_state.combo, state == STATE_BATTLE)
            renderer.update(dt)

            if state == STATE_BATTLE:
                battle.update(dt)

                # Typing challenge
                challenge_result = typing_challenge.update(dt, game_state.wave)
                if challenge_result == "timeout":
                    renderer.add_player_line("  [TIMEOUT] Challenge expired", (255, 60, 60))

                # Check for player death
                if game_state.is_dead():
                    if game_state.can_revive():
                        game_state.revive()
                        renderer.add_player_line(
                            "  [RUBBER DUCK] Revived! Keep fighting!", (255, 215, 0))
                        effects.flash_screen((255, 255, 0), 0.2)
                        sound_mgr.play_achievement()
                    else:
                        state = STATE_DEATH
                        effects.start_death_sequence()
                        sound_mgr.play_death()

                # Check wave clear
                if battle.is_wave_clear():
                    if battle.is_run_complete():
                        # Award relic
                        game_state.runs_completed += 1
                        available_relics = [r for r in RELICS if r['id'] not in game_state.relics]
                        if available_relics:
                            relic = random.choice(available_relics)
                            game_state.add_relic(relic['id'])
                            run_stats = [
                                ("Waves Cleared", str(game_state.wave)),
                                ("Enemies Killed", str(game_state.total_enemies_killed)),
                                ("LOC Earned", str(int(game_state.total_loc))),
                                ("Perks Collected", str(len(game_state.perks))),
                                ("", ""),
                                ("NEW RELIC", f"{relic['name']}: {relic['description']}"),
                            ]
                        else:
                            run_stats = [
                                ("Waves Cleared", str(game_state.wave)),
                                ("Enemies Killed", str(game_state.total_enemies_killed)),
                                ("LOC Earned", str(int(game_state.total_loc))),
                            ]
                        game_state.save()
                        state = STATE_RUN_COMPLETE
                    else:
                        # Perk choice
                        owned_ids = [p['id'] for p in game_state.perks]
                        perk_choices = get_perk_choices(owned_ids)
                        perk_selected = 0
                        state = STATE_PERK_CHOICE

            # Milestones
            while game_state.pending_milestones:
                msg = game_state.pending_milestones.pop(0)
                renderer.add_player_line(f"  *** {msg} ***", (255, 215, 0))
                sound_mgr.play_achievement()

        # --- Render ---
        render_surface.fill((5, 5, 10))

        # Matrix rain background
        particles.draw_matrix_rain(render_surface)

        # Dust
        particles.draw_dust(render_surface)

        if state == STATE_BATTLE:
            # Panels
            renderer.draw_panels(render_surface, game_state, battle.enemy, effects)
            renderer.draw_hp_bars(render_surface, game_state, battle.enemy)
            renderer.draw_player_terminal(render_surface, typing_challenge)
            renderer.draw_enemy_terminal(render_surface, battle.enemy)
            renderer.draw_bottom_bar(render_surface, game_state, game_state.wave,
                                      game_state.perks)
            renderer.draw_combo_display(render_surface, game_state.combo,
                                         game_state.is_epic_mode())

            # Particles and effects
            particles.draw_particles(render_surface)
            particles.draw_damage_numbers(render_surface)
            effects.draw_wave_text(render_surface)

        elif state == STATE_PERK_CHOICE:
            # Draw battle bg dimmed
            renderer.draw_panels(render_surface, game_state, battle.enemy, effects)
            renderer.draw_perk_choice(render_surface, perk_choices, perk_selected)

        elif state == STATE_SHOP:
            renderer.draw_panels(render_surface, game_state, battle.enemy, effects)
            renderer.draw_shop(render_surface, shop_items, game_state, shop_selected)

        elif state == STATE_DEATH:
            effects.draw_death_sequence(render_surface)

        elif state == STATE_RUN_COMPLETE:
            renderer.draw_run_stats(render_surface, run_stats)

        # Screen flash
        effects.draw_screen_flash(render_surface)

        # Glitch
        effects.draw_glitch(render_surface)

        # CRT overlay
        effects.draw_crt_overlay(render_surface)

        # Screen shake
        ox, oy = effects.get_shake_offset()
        screen.fill((0, 0, 0))
        screen.blit(render_surface, (ox, oy))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def _handle_battle_key(event, game_state, typing_challenge, battle, renderer, effects, sound_mgr):
    if game_state.input_disabled_timer > 0:
        if event.unicode and event.unicode.isprintable():
            sound_mgr.play_wrong_click()
            effects.add_trauma(0.02)
        return

    if event.unicode and event.unicode.isprintable():
        char = event.unicode

        # Every keypress always deals mash damage — nothing stops this
        battle.handle_mash_key(char)

        # Additionally, try to advance the typing challenge (pure bonus, no penalty)
        if typing_challenge.active:
            result = typing_challenge.type_char(char)
            if isinstance(result, dict):
                # Challenge completed — big bonus damage/action
                battle.handle_challenge_complete(result)


def _handle_resize(w, h, effects, particles, renderer):
    effects.resize(w, h)
    particles.resize(w, h)
    renderer.resize(w, h)


def _apply_shop_item(item, game_state):
    action = item['action']
    if action == 'heal':
        game_state.heal(item['value'])
    elif action == 'full_heal':
        game_state.hp = game_state.max_hp
        game_state.display_hp = float(game_state.max_hp)
        game_state.ghost_hp = float(game_state.max_hp)
    elif action == 'temp_buff':
        game_state.temp_buffs.append(item['value'])
    elif action == 'max_hp':
        game_state.max_hp += item['value']
        game_state.hp += item['value']
        game_state.display_hp = float(game_state.hp)
        game_state.ghost_hp = float(game_state.hp)


if __name__ == "__main__":
    main()
