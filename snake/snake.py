#!/usr/bin/env python3
"""A terminal Snake game with 3D title screen, green food, red bombs,
and full-space environment. Uses ANSI escape codes."""

import os
import sys
import time
import random

# ANSI escape codes
CLEAR = '\033[2J'
HOME = '\033[H'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'
RESET = '\033[0m'
GREEN = '\033[32m'
RED = '\033[31m'
BOLD = '\033[1m'
CYAN = '\033[36m'
GREEN_BG = '\033[42m'
RED_BG = '\033[41m'

# Game constants
WIDTH = 80
HEIGHT = 24
INITIAL_SPEED = 0.3


def clear_screen():
    sys.stdout.write(CLEAR)
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


def get_key():
    """Cross-platform non-blocking key press."""
    try:
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                return ch2
            return ch
    except ImportError:
        pass
    
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
                        ch = '\x1b[' + ch3
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except ImportError:
        pass
    
    return None


class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
    
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            return False
        
        if new_head in self.body:
            return False
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True
    
    def grow_snake(self):
        self.grow = True
    
    def set_direction(self, dx, dy):
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.direction = (dx, dy)


class Food:
    def __init__(self, snake=None):
        self.position = None
        self.bomb_position = None
        self.spawn(snake)
    
    def spawn(self, snake=None):
        while True:
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            pos = (x, y)
            if snake is None or pos not in snake.body:
                self.position = pos
                break
        
        while True:
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            pos = (x, y)
            if snake is None or pos not in snake.body:
                self.bomb_position = pos
                break


def draw_title():
    """Draw the 3D title screen using ASCII art."""
    clear_screen()
    
    # Big 3D-style Snake text using ASCII block characters
    title = [
        "  +==================================================+",
        "  ||  ########    ########    ########    ########  ||",
        "  ||  ##    ##  ##          ##          ##    ##   ||",
        "  ||  ##    ##  ##          ##          ##    ##   ||",
        "  ||  ########   ######      ######      ########   ||",
        "  ||  ##    ##  ##          ##          ##    ##   ||",
        "  ||  ##    ##  ##          ##          ##    ##   ||",
        "  ||  ########    ########    ########    ##    ##  ||",
        "  +==================================================+",
        "",
        "                      SNAKE",
        "",
        f"{CYAN}        PRESS ANY KEY TO START{RESET}",
    ]
    
    for line in title:
        sys.stdout.write(line + '\n')
        sys.stdout.flush()
    
    time.sleep(1)


def draw_game(snake, food, score, high_score):
    """Draw the game board with full-space environment."""
    clear_screen()
    
    grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    for pos in snake.body:
        x, y = pos
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            grid[y][x] = '#'
    
    x, y = food.position
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        grid[y][x] = f"{GREEN}*{RESET}"
    
    x, y = food.bomb_position
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        grid[y][x] = f"{RED}@*{RESET}"
    
    for row in grid:
        line = ''.join(row)
        sys.stdout.write(line + '\n')
    
    sys.stdout.write(f'\n{RESET}Score: {score}   High Score: {high_score}\n')
    sys.stdout.write(f'{CYAN}WASD/Arrows to move, Q to quit, P to pause.{RESET}\n')
    sys.stdout.flush()


def draw_game_over(score, high_score):
    """Draw game over screen with retry option."""
    clear_screen()
    
    sys.stdout.write(f"{BOLD}" + "=" * (WIDTH + 4) + f"{RESET}\n")
    sys.stdout.write(f"  {RED}GAME OVER!{RESET}\n")
    sys.stdout.write(f"{BOLD}" + "=" * (WIDTH + 4) + f"{RESET}\n")
    sys.stdout.write(f"\n  Final Score: {CYAN}{score}{RESET}\n")
    sys.stdout.write(f"  High Score: {CYAN}{high_score}{RESET}\n")
    sys.stdout.write(f"\n  {GREEN}R{RESET} - Retry  {RED}Q{RESET} - Quit\n")
    sys.stdout.flush()


def load_high_score():
    try:
        with open('snake_highscore.txt', 'r', encoding='utf-8') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open('snake_highscore.txt', 'w', encoding='utf-8') as f:
            f.write(str(score))
    except Exception:
        pass


def main():
    high_score = load_high_score()
    snake = Snake()
    food = Food(snake)
    score = 0
    speed = INITIAL_SPEED
    paused = False
    game_over = False
    
    draw_title()
    
    while True:
        key = get_key()
        if key:
            if isinstance(key, bytes):
                key = key.decode('ascii', errors='ignore').lower()
            
            if key == 'q':
                break
            elif key == 'r' and game_over:
                snake = Snake()
                food = Food(snake)
                score = 0
                speed = INITIAL_SPEED
                paused = False
                game_over = False
                continue
            elif key == 'p' and not game_over:
                paused = not paused
            elif not paused and not game_over:
                if key in ('w', 'up', '\x1b[A'):
                    snake.set_direction(0, -1)
                elif key in ('s', 'down', '\x1b[B'):
                    snake.set_direction(0, 1)
                elif key in ('a', 'left', '\x1b[D'):
                    snake.set_direction(-1, 0)
                elif key in ('d', 'right', '\x1b[C'):
                    snake.set_direction(1, 0)
        
        if paused and not game_over:
            draw_game(snake, food, score, high_score)
            sys.stdout.write(f'\n{RESET}Paused... Press P to resume.{RESET}\n')
            sys.stdout.flush()
            time.sleep(0.1)
            continue
        
        if game_over:
            draw_game_over(score, high_score)
            sys.stdout.flush()
            time.sleep(0.1)
            continue
        
        if not snake.move():
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_over = True
            continue
        
        if snake.body[0] == food.position:
            snake.grow_snake()
            score += 1
            food.spawn(snake)
            speed = max(0.05, INITIAL_SPEED - score * 0.003)
        
        if snake.body[0] == food.bomb_position:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_over = True
            continue
        
        draw_game(snake, food, score, high_score)
        sys.stdout.flush()
        time.sleep(speed)
    
    show_cursor()
    clear_screen()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
        sys.exit(0)