#!/usr/bin/env python3
"""Main module for Snake game: game controller, menus, and application entry point."""

import os
import sys
import time
import random

import storage
import entities
import levels
import renderer

BOARD_WIDTH = 46
BOARD_HEIGHT = 18


def get_key():
    """Cross-platform non-blocking key capture for Windows and Unix."""
    try:
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                arrow_map = {
                    b'H': 'up',
                    b'P': 'down',
                    b'K': 'left',
                    b'M': 'right',
                }
                return arrow_map.get(ch2, None)
            return ch
        return None
    except ImportError:
        pass

    if sys.platform != 'win32':
        try:
            import select
            fd = sys.stdin.fileno()
            if select.select([sys.stdin], [], [], 0)[0]:
                import tty
                import termios
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            ch3 = sys.stdin.read(1)
                            arrow_codes = {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}
                            return arrow_codes.get(ch3, '\x1b[' + ch3)
                    return ch
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (ImportError, Exception):
            pass

    return None


def run_game_session(mode: str, settings: dict):
    """Run active game loop for either 10-Level Classic Campaign or Endless Random Mode."""
    leaderboard = storage.load_leaderboard()
    best_score = leaderboard[0] if leaderboard else 0
    snake_color = settings.get("color", "Green")

    start_pos = (BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
    snake = entities.create_snake(start_pos, color=snake_color)

    score = 0
    current_level = 1
    level_food_eaten = 0
    obstacles = set()
    req_food = 0
    level_name = ""

    if mode == "classic":
        lvl_data = levels.get_level_data(current_level, BOARD_WIDTH, BOARD_HEIGHT)
        level_name = f"Level {current_level}/10: {lvl_data['name']}"
        req_food = lvl_data['required_food']
        obstacles = set(lvl_data['obstacles'])
    else:
        level_name = "Endless: Random Mode"
        req_food = 0

    foods = [entities.spawn_food(snake.body, obstacles, BOARD_WIDTH, BOARD_HEIGHT)]
    speed = 0.15
    paused = False
    ticks = 0

    while True:
        key = get_key()
        if key:
            if isinstance(key, bytes):
                key = key.decode('ascii', errors='ignore').lower()

            if key == 'q':
                break
            elif key == 'p':
                paused = not paused
            elif not paused:
                if key in ('w', 'up'):
                    entities.change_snake_direction(snake, (0, -1))
                elif key in ('s', 'down'):
                    entities.change_snake_direction(snake, (0, 1))
                elif key in ('a', 'left'):
                    entities.change_snake_direction(snake, (-1, 0))
                elif key in ('d', 'right'):
                    entities.change_snake_direction(snake, (1, 0))

        if paused:
            hud_data = {
                "score": score,
                "best": max(best_score, score),
                "mode_name": level_name,
                "food_count": level_food_eaten,
                "req_food": req_food
            }
            renderer.draw_game_board(snake, foods, obstacles, hud_data, BOARD_WIDTH, BOARD_HEIGHT, paused=True)
            time.sleep(0.1)
            continue

        ticks += 1

        # Advance snake
        new_head = entities.move_snake(snake)

        # Check collision with boundary walls or obstacles
        if levels.check_collision(new_head, obstacles, BOARD_WIDTH, BOARD_HEIGHT):
            break

        # Check self collision (head with any body segment after index 0)
        if new_head in snake.body[1:]:
            break

        # Check item pickups
        eaten_item = None
        for item in foods:
            if new_head == item.pos:
                eaten_item = item
                break

        if eaten_item:
            score += eaten_item.points
            snake.grow_pending += eaten_item.bonus_len
            foods.remove(eaten_item)

            if eaten_item.kind == 'food':
                level_food_eaten += 1
                # Spawn next regular food
                foods.append(entities.spawn_food(snake.body, obstacles, BOARD_WIDTH, BOARD_HEIGHT))

                # Periodic special/bonus food spawn
                if random.random() < 0.35 and len(foods) < 3:
                    occ = {f.pos for f in foods}
                    sp = entities.spawn_special_food(snake.body, obstacles, occ, BOARD_WIDTH, BOARD_HEIGHT)
                    if sp:
                        foods.append(sp)

                # Classic Mode progression
                if mode == "classic" and level_food_eaten >= req_food:
                    if current_level < levels.get_total_levels():
                        current_level += 1
                        level_food_eaten = 0
                        lvl_data = levels.get_level_data(current_level, BOARD_WIDTH, BOARD_HEIGHT)
                        level_name = f"Level {current_level}/10: {lvl_data['name']}"
                        req_food = lvl_data['required_food']
                        obstacles = set(lvl_data['obstacles'])
                        foods = [entities.spawn_food(snake.body, obstacles, BOARD_WIDTH, BOARD_HEIGHT)]
                    else:
                        # Completed all 10 levels!
                        level_name = "Grand Master Achieved!"
                        break

                # Random Mode obstacle buildup
                if mode == "random" and level_food_eaten % 3 == 0:
                    new_obs = levels.generate_random_obstacles(len(obstacles) + 2, snake.body, BOARD_WIDTH, BOARD_HEIGHT)
                    obstacles.update(new_obs)

            # Speed adjustment as score rises
            speed = max(0.06, 0.15 - (score * 0.0015))

        # Update lifetimes of timed bonus/special foods
        expired = []
        for f in foods:
            if f.lifetime > 0:
                f.lifetime -= 1
                if f.lifetime <= 0:
                    expired.append(f)
        for exp in expired:
            foods.remove(exp)

        hud_data = {
            "score": score,
            "best": max(best_score, score),
            "mode_name": level_name,
            "food_count": level_food_eaten,
            "req_food": req_food
        }
        renderer.draw_game_board(snake, foods, obstacles, hud_data, BOARD_WIDTH, BOARD_HEIGHT, paused=False)
        time.sleep(speed)

    # Session over: record score and show end screen
    storage.add_high_score(score)
    renderer.clear_screen()
    print(renderer.get_ascii_title())
    print("\n" + f"{renderer.BOLD}{renderer.RED}=== GAME OVER ==={renderer.RESET}")
    print(f"\nFinal Score: {renderer.BRIGHT_CYAN}{score}{renderer.RESET}")
    print(f"Top High Score: {renderer.YELLOW}{max(best_score, score)}{renderer.RESET}\n")
    print(f"{renderer.BRIGHT_BLUE}Press any key to return to menu...{renderer.RESET}")

    time.sleep(0.5)
    while get_key() is not None:
        pass
    while True:
        if get_key():
            break
        time.sleep(0.05)


def handle_settings_menu(settings: dict):
    """Handle interactive snake color customization menu."""
    colors = ["Green", "Cyan", "Magenta"]
    current_color = settings.get("color", "Green")
    selected_idx = colors.index(current_color) if current_color in colors else 0

    while True:
        # Build color options with ooO preview in appropriate color
        options = []
        for c in colors:
            code = renderer.COLOR_MAP.get(c, renderer.BRIGHT_GREEN)
            options.append(f"{code}ooO{renderer.RESET} {c}")

        renderer.draw_menu(
            options=options,
            selected_idx=selected_idx,
            header_text="Choose your snake colour:",
            footer_text="Use Up/Down to choose, Enter to confirm."
        )

        while True:
            k = get_key()
            if k:
                if isinstance(k, bytes):
                    k = k.decode('ascii', errors='ignore').lower()
                if k in ('w', 'up'):
                    selected_idx = (selected_idx - 1) % len(colors)
                    break
                elif k in ('s', 'down'):
                    selected_idx = (selected_idx + 1) % len(colors)
                    break
                elif k in ('\r', '\n', ' ', 'enter'):
                    settings["color"] = colors[selected_idx]
                    storage.save_settings(settings)
                    return
                elif k == 'q':
                    return
            time.sleep(0.05)


def main():
    """Application entry point: main navigation menu orchestrator."""
    if sys.platform == 'win32':
        os.system('')

    sys.stdout.write(renderer.HIDE_CURSOR)
    sys.stdout.flush()

    settings = storage.load_settings()

    try:
        main_options = ["Play Game", "High Score", "Instructions", "Settings", "Exit"]
        selected_idx = 0

        while True:
            leaderboard = storage.load_leaderboard()
            best_score = leaderboard[0] if leaderboard else 0

            renderer.draw_menu(
                options=main_options,
                selected_idx=selected_idx,
                best_score=best_score,
                footer_text="Use Up/Down (or W/S) to choose, Enter to select."
            )

            # Menu navigation loop
            chosen_action = None
            while True:
                k = get_key()
                if k:
                    if isinstance(k, bytes):
                        k = k.decode('ascii', errors='ignore').lower()
                    if k in ('w', 'up'):
                        selected_idx = (selected_idx - 1) % len(main_options)
                        break
                    elif k in ('s', 'down'):
                        selected_idx = (selected_idx + 1) % len(main_options)
                        break
                    elif k in ('\r', '\n', ' ', 'enter'):
                        chosen_action = main_options[selected_idx]
                        break
                    elif k == 'q':
                        chosen_action = "Exit"
                        break
                time.sleep(0.05)

            if chosen_action == "Play Game":
                # Mode selection sub-menu
                mode_options = ["Random Mode  (Endless)", "Classic Mode (10 Levels)", "Back to Main Menu"]
                mode_idx = 0
                while True:
                    if mode_idx == 0:
                        info = "Random Mode: obstacles build up endlessly as your score grows"
                    elif mode_idx == 1:
                        info = "Classic Mode: fight through 10 hand-built levels to become a grand master."
                    else:
                        info = ""

                    renderer.draw_menu(
                        options=mode_options,
                        selected_idx=mode_idx,
                        header_text="Choose your game mode:",
                        footer_text="Use Up/Down (or W/S) to choose, Enter to select.",
                        extra_info=info
                    )

                    mode_action = None
                    while True:
                        mk = get_key()
                        if mk:
                            if isinstance(mk, bytes):
                                mk = mk.decode('ascii', errors='ignore').lower()
                            if mk in ('w', 'up'):
                                mode_idx = (mode_idx - 1) % len(mode_options)
                                break
                            elif mk in ('s', 'down'):
                                mode_idx = (mode_idx + 1) % len(mode_options)
                                break
                            elif mk in ('\r', '\n', ' ', 'enter'):
                                mode_action = mode_idx
                                break
                            elif mk == 'q':
                                mode_action = 2
                                break
                        time.sleep(0.05)

                    if mode_action == 0:
                        run_game_session("random", settings)
                        break
                    elif mode_action == 1:
                        run_game_session("classic", settings)
                        break
                    elif mode_action == 2:
                        break

            elif chosen_action == "High Score":
                renderer.draw_leaderboard_screen(storage.load_leaderboard())
                time.sleep(0.3)
                while get_key() is not None:
                    pass
                while True:
                    if get_key():
                        break
                    time.sleep(0.05)

            elif chosen_action == "Instructions":
                renderer.draw_instructions_screen()
                time.sleep(0.3)
                while get_key() is not None:
                    pass
                while True:
                    if get_key():
                        break
                    time.sleep(0.05)

            elif chosen_action == "Settings":
                handle_settings_menu(settings)

            elif chosen_action == "Exit":
                break

    finally:
        sys.stdout.write(renderer.SHOW_CURSOR)
        sys.stdout.flush()
        renderer.clear_screen()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write(renderer.SHOW_CURSOR)
        sys.stdout.flush()
        renderer.clear_screen()
        sys.exit(0)