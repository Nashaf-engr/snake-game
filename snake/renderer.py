"""Renderer module for Snake game: ANSI terminal UI, menus, and game board display."""

import os
import sys
from typing import List, Tuple, Dict, Any, Optional

# ANSI Escape Sequences
CLEAR = '\033[2J'
HOME = '\033[H'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[32m'
BRIGHT_GREEN = '\033[92m'
CYAN = '\033[36m'
BRIGHT_CYAN = '\033[96m'
MAGENTA = '\033[35m'
BRIGHT_MAGENTA = '\033[95m'
YELLOW = '\033[33m'
RED = '\033[31m'
BLUE = '\033[34m'
BRIGHT_BLUE = '\033[94m'
WHITE = '\033[37m'
GRAY = '\033[90m'

COLOR_MAP = {
    "Green": BRIGHT_GREEN,
    "Cyan": BRIGHT_CYAN,
    "Magenta": BRIGHT_MAGENTA
}


def clear_screen():
    """Cross-platform flicker-free terminal screen clear."""
    if os.name == 'nt':
        os.system('cls')
    else:
        sys.stdout.write(CLEAR + HOME)
        sys.stdout.flush()


def get_ascii_title() -> str:
    """Return stylized green ASCII art logo for Snake."""
    lines = [
        r"   _____             _        ",
        r"  / ____|           | |       ",
        r" | (___  _ __   __ _| | _____ ",
        r"  \___ \| '_ \ / _` | |/ / _ \ ",
        r"  ____) | | | | (_| |   <  __/",
        r" |_____/|_| |_|\__,_|_|\_\___|",
    ]
    return '\n'.join(f"{BRIGHT_GREEN}{line}{RESET}" for line in lines)


def draw_menu(options: List[str], selected_idx: int, header_text: str = "",
              footer_text: str = "Use Up/Down (or W/S) to choose, Enter to select.",
              extra_info: Optional[str] = None, best_score: Optional[int] = None):
    """Render interactive main menu, mode select, and settings screens."""
    clear_screen()
    buffer = []
    buffer.append(get_ascii_title())
    buffer.append("")

    if best_score is not None:
        buffer.append(f"{WHITE}Best Score: {YELLOW}{best_score}{RESET}")
        buffer.append("")

    if header_text:
        buffer.append(f"{WHITE}{header_text}{RESET}")
        buffer.append("")

    for i, opt in enumerate(options):
        if i == selected_idx:
            buffer.append(f" {BRIGHT_GREEN}> {opt}{RESET}")
        else:
            buffer.append(f"   {WHITE}{opt}{RESET}")

    buffer.append("")
    if extra_info:
        buffer.append(f"{CYAN}{extra_info}{RESET}")
        buffer.append("")

    if footer_text:
        buffer.append(f"{BRIGHT_BLUE}{footer_text}{RESET}")

    sys.stdout.write('\n'.join(buffer) + '\n')
    sys.stdout.flush()


def draw_game_board(snake, foods: list, obstacles: set,
                    hud_data: Dict[str, Any], width: int, height: int, paused: bool = False):
    """Render the full in-game view: top HUD, blue framed boundary box, and bottom legend."""
    lines = []

    # Top HUD
    score = hud_data.get("score", 0)
    best = hud_data.get("best", 0)
    pause_str = f"  {RED}[PAUSED]{RESET}" if paused else ""
    hud_line_1 = f"Score: {WHITE}{score:<8}{RESET}Best: {YELLOW}{best:<8}{RESET}{pause_str}"
    lines.append(hud_line_1)

    mode_name = hud_data.get("mode_name", "")
    food_count = hud_data.get("food_count", 0)
    req_food = hud_data.get("req_food", 0)
    if req_food > 0:
        hud_line_2 = f"{CYAN}{mode_name:<28}{RESET}Food: {WHITE}{food_count}/{req_food}{RESET}"
    else:
        hud_line_2 = f"{CYAN}{mode_name:<28}{RESET}Food: {WHITE}{food_count}{RESET}"
    lines.append(hud_line_2)

    # Blue border box
    border_top = f"{BRIGHT_BLUE}+{'-' * width}+{RESET}"
    lines.append(border_top)

    # Coordinate lookup sets/maps
    snake_color_code = COLOR_MAP.get(snake.color, BRIGHT_GREEN)
    snake_head = snake.body[0]
    snake_body_set = set(snake.body[1:])

    # Head character based on direction
    dx, dy = snake.direction
    if dx == 1:
        head_char = ">"
    elif dx == -1:
        head_char = "<"
    elif dy == -1:
        head_char = "^"
    else:
        head_char = "v"

    food_map = {f.pos: f for f in foods}

    for y in range(height):
        row_chars = []
        for x in range(width):
            pos = (x, y)
            if pos == snake_head:
                row_chars.append(f"{snake_color_code}{head_char}{RESET}")
            elif pos in snake_body_set:
                # Alternate body pattern ~ and =
                idx = snake.body.index(pos)
                body_char = "=" if idx % 2 == 1 else "~"
                row_chars.append(f"{snake_color_code}{body_char}{RESET}")
            elif pos in food_map:
                item = food_map[pos]
                if item.kind == 'food':
                    row_chars.append(f"{RED}*{RESET}")
                elif item.kind == 'bonus':
                    row_chars.append(f"{YELLOW}+{RESET}")
                elif item.kind == 'special':
                    row_chars.append(f"{BRIGHT_CYAN}${RESET}")
                else:
                    row_chars.append(f"{RED}*{RESET}")
            elif pos in obstacles:
                row_chars.append(f"{GRAY}#{RESET}")
            else:
                row_chars.append(' ')
        lines.append(f"{BRIGHT_BLUE}|{RESET}{''.join(row_chars)}{BRIGHT_BLUE}|{RESET}")

    border_bottom = f"{BRIGHT_BLUE}+{'-' * width}+{RESET}"
    lines.append(border_bottom)

    # Bottom helper legend
    lines.append(f"{CYAN}Arrows/WASD: move   P: pause   Q: quit to menu{RESET}")
    legend = (
        f"{RED}* food{RESET}   "
        f"{YELLOW}+ bonus +5{RESET}   "
        f"{BRIGHT_CYAN}$ special +10/+5len{RESET}   "
        f"{GRAY}# obstacle{RESET}"
    )
    lines.append(legend)

    clear_screen()
    sys.stdout.write('\n'.join(lines) + '\n')
    sys.stdout.flush()


def draw_leaderboard_screen(scores: List[int]):
    """Render Top-5 High Score leaderboard screen."""
    clear_screen()
    lines = [
        get_ascii_title(),
        "",
        f"{BOLD}{WHITE}=== Top-5 High Score Leaderboard ==={RESET}",
        ""
    ]
    medals = ["1st", "2nd", "3rd", "4th", "5th"]
    for i in range(5):
        val = scores[i] if i < len(scores) else 0
        medal = medals[i]
        lines.append(f"   {YELLOW}{medal:<5}{RESET} : {WHITE}{val:>5} pts{RESET}")

    lines.append("")
    lines.append(f"{BRIGHT_BLUE}Press any key to return to menu.{RESET}")
    sys.stdout.write('\n'.join(lines) + '\n')
    sys.stdout.flush()


def draw_instructions_screen():
    """Render Instructions & Rules screen."""
    clear_screen()
    lines = [
        get_ascii_title(),
        "",
        f"{BOLD}{WHITE}=== Game Instructions ==={RESET}",
        "",
        f"{CYAN}Controls:{RESET}",
        "  - WASD or Arrow Keys : Move Snake",
        "  - P                   : Pause / Resume",
        "  - Q                   : Quit to Menu",
        "",
        f"{CYAN}Game Items:{RESET}",
        f"  - {RED}* Food{RESET}     : +1 Score, grows snake by 1",
        f"  - {YELLOW}+ Bonus{RESET}    : +5 Score (timed)",
        f"  - {BRIGHT_CYAN}$ Special{RESET}  : +10 Score, grows snake by 5 (timed)",
        f"  - {GRAY}# Obstacle{RESET} : Wall/Hazard. Avoid hitting these!",
        "",
        f"{CYAN}Modes:{RESET}",
        "  - Classic Mode : Complete 10 hand-built geometric maze levels.",
        "  - Random Mode  : Endless gameplay where obstacles build up as you score.",
        "",
        f"{BRIGHT_BLUE}Press any key to return to menu.{RESET}"
    ]
    sys.stdout.write('\n'.join(lines) + '\n')
    sys.stdout.flush()
