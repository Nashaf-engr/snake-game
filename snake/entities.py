"""Entities module for Snake game: custom structs and entity management."""

import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class Position:
    x: int
    y: int

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


@dataclass
class SnakeEntity:
    body: List[Tuple[int, int]]
    direction: Tuple[int, int] = (1, 0)
    color: str = "Green"
    grow_pending: int = 0


@dataclass
class FoodEntity:
    pos: Tuple[int, int]
    kind: str           # 'food' (*), 'bonus' (+), 'special' ($)
    points: int
    bonus_len: int
    lifetime: int       # ticks remaining, -1 for infinite


def create_snake(start_pos: Tuple[int, int], color: str = "Green") -> SnakeEntity:
    """Initialize a Snake entity with starting position and color."""
    x, y = start_pos
    # Snake initially with 3 segments moving right: head at (x, y), body trailing left
    body = [(x, y), (x - 1, y), (x - 2, y)]
    return SnakeEntity(body=body, direction=(1, 0), color=color, grow_pending=0)


def move_snake(snake: SnakeEntity, grow_amount: int = 0) -> Tuple[int, int]:
    """Advance the snake head by direction and manage tail growth."""
    snake.grow_pending += grow_amount
    head_x, head_y = snake.body[0]
    dx, dy = snake.direction
    new_head = (head_x + dx, head_y + dy)
    snake.body.insert(0, new_head)
    if snake.grow_pending > 0:
        snake.grow_pending -= 1
    else:
        snake.body.pop()
    return new_head


def change_snake_direction(snake: SnakeEntity, new_dir: Tuple[int, int]) -> bool:
    """Safely update snake direction preventing 180-degree self reversals."""
    dx, dy = new_dir
    cur_dx, cur_dy = snake.direction
    if len(snake.body) > 1 and (dx, dy) == (-cur_dx, -cur_dy):
        return False
    snake.direction = new_dir
    return True


def spawn_food(snake_body: List[Tuple[int, int]], obstacles: set, width: int, height: int) -> FoodEntity:
    """Spawn standard food (*) at an unoccupied position."""
    occupied = set(snake_body) | obstacles
    available = [(x, y) for x in range(width) for y in range(height) if (x, y) not in occupied]
    if not available:
        pos = (width // 2, height // 2)
    else:
        pos = random.choice(available)
    return FoodEntity(pos=pos, kind='food', points=1, bonus_len=1, lifetime=-1)


def spawn_special_food(snake_body: List[Tuple[int, int]], obstacles: set,
                       occupied_positions: set, width: int, height: int) -> Optional[FoodEntity]:
    """Spawn either a bonus (+5 score) or special ($ +10 score / +5 length) item with limited lifetime."""
    occupied = set(snake_body) | obstacles | occupied_positions
    available = [(x, y) for x in range(width) for y in range(height) if (x, y) not in occupied]
    if not available:
        return None
    pos = random.choice(available)
    # 60% chance bonus (+), 40% chance special ($)
    if random.random() < 0.6:
        return FoodEntity(pos=pos, kind='bonus', points=5, bonus_len=1, lifetime=45)
    else:
        return FoodEntity(pos=pos, kind='special', points=10, bonus_len=5, lifetime=35)
