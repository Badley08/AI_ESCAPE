# Level 1 — TEST ALPHA: Damage & Collision System

RTB-O9 must survive 60 seconds of canon fire. Canons deal **5 dmg** per hit. Primary color: **blue**.

## Proposed Changes

### Player — Damage & Collision

#### [MODIFY] [player.py](file:///home/luberisse/Bureau/Canon_Evasion/src/player.py)

- Fix the broken `move_right` collision check (`self.game.game.check.collision` → `self.game.check_collision`)
- Add a `damage(amount)` method that reduces health (clamped to `min_health`)
- Add an `is_alive` property (`health > min_health`)
- Remove the duplicate `self.rect = self.image.get_rect()` line
- Keep neutral comments like the existing code

---

### Game — Collision Loop, Timer, State Machine

#### [MODIFY] [game.py](file:///home/luberisse/Bureau/Canon_Evasion/src/game.py)

- Pass `self` to `Player(self)` so the player has a game reference
- Add a **60-second countdown timer** (`self.timer = 60`, tracked with `pygame.time.get_ticks()`)
- Add game states: `playing`, `game_over`, `victory`
- In an `update()` method each frame:
  - Decrement timer
  - For each canon, check collision between all its projectiles and the player
  - On collision: deal 5 dmg, remove projectile, spawn explosion effect, show damage flash
  - If `player.health <= 0` → state = `game_over`
  - If `timer <= 0` and player alive → state = `victory`
- Store a group for explosion sprites (visual effects)

---

### Projectile — Damage Value

#### [MODIFY] [projectiles.py](file:///home/luberisse/Bureau/Canon_Evasion/src/projectiles.py)

- Add `self.damage = 5` to projectiles
- Add neutral comments

---

### Explosion Effect (NEW)

#### [NEW] [explosion.py](file:///home/luberisse/Bureau/Canon_Evasion/src/explosion.py)

- A simple sprite that displays `explosion.png` at the collision point
- Auto-removes itself after ~15 frames (brief visual flash)

---

### HUD — Health Bar, Timer, Intro Text

#### [NEW] [hud.py](file:///home/luberisse/Bureau/Canon_Evasion/src/hud.py)

- **Health bar**: drawn as a blue bar (primary color) at top-left, shows `player.health / max_health`
- **Countdown timer**: large text top-center showing remaining seconds (`60`, `59`…`0`)
- **Level title**: "TEST ALPHA" displayed briefly at start
- **Objective text**: "Survive 60 seconds" shown at the beginning for a few seconds
- **Damage overlay**: flash `damage.png` briefly on screen when player takes a hit
- Uses `pygame.font.Font(None, size)` since SysFont might time out

---

### Main Loop — Integrate Everything

#### [MODIFY] [main.py](file:///home/luberisse/Bureau/Canon_Evasion/src/main.py)

- Import the new HUD module
- Call `game.update()` each frame to run collision/timer logic
- Draw HUD elements (health bar, timer, texts)
- When `game.state == "game_over"`:
  - Display `game_over.png` centered on screen
  - Stop game logic, wait for keypress or quit
- When `game.state == "victory"`:
  - Display `victory.png` centered on screen
  - Stop game logic, wait for keypress or quit
- Add FPS cap with `clock.tick(60)`

---

## Asset Usage Summary

| Asset | Purpose |
|---|---|
| `tir.png` | Already used as projectile sprite |
| `damage.png` | Flash overlay when player takes damage |
| `explosion.png` | Spawned at collision point briefly |
| `game_over.png` | Full screen when health reaches 0 |
| `victory.png` | Full screen when timer reaches 0 (survived!) |

## Verification Plan

### Manual Verification
- Run `./env/bin/python main.py` from `src/` directory
- Confirm projectiles collide with the player and deal 5 dmg
- Confirm health bar decreases and damage/explosion effects show
- Confirm 60-second countdown is visible
- Confirm game over screen appears when health = 0
- Confirm victory screen appears when timer = 0 while alive
