#!/usr/bin/env python3
"""A lightweight terminal Snake game using ANSI escape codes."""

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

# Game constants
WIDTH = 20
HEIGHT = 15
INITIAL_SPEED = 0.25


def clear_screen():
    sys.stdout.write(CLEAR + HOME)
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


def draw(snake, food, score, high_score):
    clear_screen()
    
    # Draw border
    print('+' + '-' * WIDTH + '+')
    for y in range(HEIGHT):
        print('|', end='')
        for x in range(WIDTH):
            pos = (x, y)
            if pos == snake.body[0]:
                print('O', end='')  # Head
            elif pos in snake.body:
                print('o', end='')  # Body
            elif pos == food.position:
                print('*', end='')  # Food
            else:
                print(' ', end='')
        print('|')
    print('+' + '-' * WIDTH + '+')
    
    print(f'Score: {score}   High Score: {high_score}')
    print('\nWASD/Arrows to move, Q to quit, P to pause.')


def get_key():
    """Cross-platform non-blocking key press."""
    try:
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            # Handle extended keys (arrows)
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                return ch2
            return ch
    except ImportError:
        pass
    
    try:
        import select
        import tty
        import termios
        fd = sys.stdin.fileno()
        if select.select([sys.stdin], [], [], 0)[0]:
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # ESC sequence for arrows
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        ch = f'\x1b[{ch3}'
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
        self.direction = (1, 0)  # (dx, dy)
        self.grow = False
    
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            return False
        
        # Check self collision
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
        # Prevent reversing into self
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.direction = (dx, dy)


class Food:
    def __init__(self, snake=None):
        self.position = None
        self.spawn(snake)
    
    def spawn(self, snake=None):
        while True:
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            pos = (x, y)
            if snake is None or pos not in snake.body:
                self.position = pos
                break


def load_high_score():
    try:
        with open('snake_highscore.txt', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open('snake_highscore.txt', 'w') as f:
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
    
    hide_cursor()
    
    while True:
        # Handle input
        key = get_key()
        if key:
            if isinstance(key, bytes):
                key = key.decode('ascii', errors='ignore').lower()
            
            # Handle arrow keys (ESC sequences)
            if key == 'q':
                break
            elif key == 'p':
                paused = not paused
            elif not paused:
                if key in ('w', 'up', '\x1b[A'):
                    snake.set_direction(0, -1)
                elif key in ('s', 'down', '\x1b[B'):
                    snake.set_direction(0, 1)
                elif key in ('a', 'left', '\x1b[D'):
                    snake.set_direction(-1, 0)
                elif key in ('d', 'right', '\x1b[C'):
                    snake.set_direction(1, 0)
        
        if paused:
            draw(snake, food, score, high_score)
            print('\nPress P to resume...')
            time.sleep(0.1)
            continue
        
        # Move snake
        if not snake.move():
            # Game over
            clear_screen()
            print('+' + '-' * WIDTH + '+')
            for y in range(HEIGHT):
                print('|', end='')
                for x in range(WIDTH):
                    if (x, y) == (WIDTH // 2, HEIGHT // 2):
                        print('X', end='')
                    else:
                        print(' ', end='')
                print('|')
            print('+' + '-' * WIDTH + '+')
            print(f'\nGame Over!')
            print(f'Final Score: {score}')
            if score > high_score:
                print(f'New High Score!')
                high_score = score
                save_high_score(high_score)
            show_cursor()
            input('\nPress Enter to exit...')
            break
        
        # Check food collision
        if snake.body[0] == food.position:
            snake.grow_snake()
            score += 1
            food.spawn(snake)
            # Increase speed slightly
            speed = max(0.05, INITIAL_SPEED - score * 0.005)
        
        draw(snake, food, score, high_score)
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