# Terminal Snake Game

A modular terminal-based Snake game featuring custom geometric mazes, endless obstacle buildup, colored items, snake customization, and persistent Top-5 high scores.

## Architecture

- **Modular Architecture**: Split across 5 separate modules with 24 custom functions:
  - `snake.py`: Application entry point, main orchestrator, game loop, and input handling.
  - `entities.py`: Game entities, custom struct types, snake motion, and item spawning.
  - `levels.py`: 10-level campaign with geometric mazes and dynamic obstacle generation.
  - `renderer.py`: ANSI terminal UI, menus, in-game framed view, and HUD.
  - `storage.py`: File persistence for Top-5 high scores and user settings.
- **Core Mechanics**: Custom struct types (`Position`, `SnakeEntity`, `FoodEntity`) with array-based body tracking.
- **Persistent Data**: File handling to save and display a Top-5 High Score leaderboard.
- **Game Modes**:
  - **Random Mode (Endless)**: Obstacles build up endlessly as score grows.
  - **Classic Mode (10 Levels)**: 10 hand-built levels with custom geometric mazes.

## Run the Game

```bash
python snake.py
```

## Controls

- **WASD** or **Arrow Keys**: Move the snake / Navigate menus
- **Enter**: Confirm selection in menus
- **P**: Pause / Resume game
- **Q**: Quit to menu

## Game Items & Legend

- `*` **Food** (Red): +1 Score, grows snake by 1 segment
- `+` **Bonus** (Yellow): +5 Score (timed)
- `$` **Special** (Cyan): +10 Score, grows snake by 5 segments (timed)
- `#` **Obstacle** (Gray): Maze hazard or obstacle. Hitting ends the run!

## Customization

Under **Settings**, choose your snake color:
- `ooO Green`
- `ooO Cyan`
- `ooO Magenta`
