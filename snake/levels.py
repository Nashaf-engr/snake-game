"""Levels module for Snake game: 10-level campaign mazes and endless random mode."""

import random
from typing import Set, Tuple, Dict, Any


def get_total_levels() -> int:
    """Return the total number of campaign levels."""
    return 10


def get_level_data(level_num: int, width: int = 46, height: int = 18) -> Dict[str, Any]:
    """Return name, required food, and custom geometric maze obstacles for a level."""
    obstacles: Set[Tuple[int, int]] = set()
    cx, cy = width // 2, height // 2

    if level_num == 1:
        name = "Open Plains"
        required_food = 6
        # Level 1 has no obstacles

    elif level_num == 2:
        name = "The Box"
        required_food = 8
        # Central square outline with gaps
        for x in range(cx - 6, cx + 7):
            if abs(x - cx) > 2:
                obstacles.add((x, cy - 4))
                obstacles.add((x, cy + 4))
        for y in range(cy - 4, cy + 5):
            if abs(y - cy) > 1:
                obstacles.add((cx - 6, y))
                obstacles.add((cx + 6, y))

    elif level_num == 3:
        name = "Four Corners"
        required_food = 10
        # 4 L-shaped corner barriers
        for i in range(2, 9):
            obstacles.add((i, 3))
            obstacles.add((width - 1 - i, 3))
            obstacles.add((i, height - 4))
            obstacles.add((width - 1 - i, height - 4))
        for j in range(3, 7):
            obstacles.add((2, j))
            obstacles.add((width - 3, j))
            obstacles.add((2, height - 1 - j))
            obstacles.add((width - 3, height - 1 - j))

    elif level_num == 4:
        name = "Twin Peaks"
        required_food = 12
        # Two vertical divider walls with pass gaps
        for y in range(2, height - 2):
            if y not in (cy - 1, cy, cy + 1):
                obstacles.add((width // 3, y))
                obstacles.add((2 * width // 3, y))

    elif level_num == 5:
        name = "The Cross"
        required_food = 14
        # Central plus/cross with gaps near center
        for x in range(8, width - 8):
            if abs(x - cx) > 4:
                obstacles.add((x, cy))
        for y in range(2, height - 2):
            if abs(y - cy) > 2:
                obstacles.add((cx, y))

    elif level_num == 6:
        name = "Labyrinth"
        required_food = 16
        # Horizontal alternating hurdles
        for x in range(4, width - 10):
            obstacles.add((x, height // 4))
            obstacles.add((width - 1 - x, 3 * height // 4))
        for x in range(10, width - 4):
            obstacles.add((x, cy))

    elif level_num == 7:
        name = "Spiral"
        required_food = 18
        # Outer and middle geometric spiral teeth
        for x in range(6, width - 6):
            obstacles.add((x, 3))
            obstacles.add((x, height - 4))
        for y in range(3, height - 6):
            obstacles.add((width - 6, y))
        for y in range(6, height - 4):
            obstacles.add((6, y))

    elif level_num == 8:
        name = "Pillars"
        required_food = 20
        # 3x2 grid of pillar blocks
        for px in [width // 4, width // 2, 3 * width // 4]:
            for py in [height // 3, 2 * height // 3]:
                obstacles.add((px, py))
                obstacles.add((px + 1, py))
                obstacles.add((px, py + 1))
                obstacles.add((px + 1, py + 1))

    elif level_num == 9:
        name = "Checkerboard"
        required_food = 22
        # Checkerboard obstacle teeth
        for x in range(5, width - 5, 8):
            for y in range(2, height - 2, 4):
                for dx in range(3):
                    for dy in range(2):
                        obstacles.add((x + dx, y + dy))

    else:
        name = "The Gauntlet"
        required_food = 25
        # Complex multi-room chamber
        for x in range(4, width - 4):
            if x not in (width // 4, 3 * width // 4):
                obstacles.add((x, height // 3))
                obstacles.add((x, 2 * height // 3))
        for y in range(height // 3, 2 * height // 3 + 1):
            if y != cy:
                obstacles.add((cx, y))

    # Safety: ensure snake start area is never obstructed
    start_area = {(x, y) for x in range(cx - 5, cx + 5) for y in range(cy - 2, cy + 3)}
    obstacles = obstacles - start_area

    return {
        "level": level_num,
        "name": name,
        "required_food": required_food,
        "obstacles": obstacles
    }


def generate_random_obstacles(count: int, snake_body: list, width: int, height: int) -> Set[Tuple[int, int]]:
    """Spawn random geometric obstacle clusters for Endless Random Mode."""
    obstacles: Set[Tuple[int, int]] = set()
    occupied = set(snake_body)
    cx, cy = width // 2, height // 2
    # Keep center spawn area clear
    safe_zone = {(x, y) for x in range(cx - 4, cx + 4) for y in range(cy - 2, cy + 2)}
    forbidden = occupied | safe_zone

    attempts = 0
    while len(obstacles) < count and attempts < 200:
        attempts += 1
        x = random.randint(2, width - 3)
        y = random.randint(1, height - 2)
        if (x, y) not in forbidden:
            obstacles.add((x, y))
    return obstacles


def check_collision(pos: Tuple[int, int], obstacles: Set[Tuple[int, int]], width: int, height: int) -> bool:
    """Check whether a position violates boundary walls or hits an obstacle."""
    x, y = pos
    if x < 0 or x >= width or y < 0 or y >= height:
        return True
    if (x, y) in obstacles:
        return True
    return False
