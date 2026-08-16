# AI_ESCAPE

A 2D game built with Python and Pygame.

## Description

The player must survive for a set amount of time while avoiding projectiles fired by canons. The game includes a splash screen, a level selection screen, and gameplay with a health bar, countdown timer, and game over / victory states.

## Requirements

- Python 3.10+
- Pygame 2.x

## Installation

```bash
pip install pygame
```

## Usage

Run the game from the `src/` directory:

```bash
cd src
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys / WASD | Move the player |
| R | Restart after game over or victory |
| ESC | Quit the game |
| Space / Click | Skip the splash screen |

## Project Structure

```
src/
├── main.py          # Entry point
├── docs/            # Project documentation
└── level1/          # Level 1 content
    ├── assets/      # Images and sprites
    ├── sounds/      # Audio files
    ├── game.py      # Game logic
    ├── player.py    # Player class
    ├── hud.py       # Heads-up display
    ├── canon.py     # Canon class
    ├── explosion.py # Explosion effect
    └── projectiles.py # Projectile class
```

## License

All rights reserved.
