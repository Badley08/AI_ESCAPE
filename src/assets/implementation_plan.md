# Implementation Plan: Splash Screen Click & Level Selection

## Goal
1. Allow the user to advance past the splash screen by clicking anywhere with the mouse, in addition to pressing the Space bar.
2. Introduce a "Level Selection" screen immediately after the splash screen using `assets/level.png`.
3. Make the "First Level" clickable to start the game, while ignoring clicks on other levels.
4. Set the actual game background to `assets/back.png` (since `level.png` was previously used by mistake).

## User Review Required
> [!IMPORTANT]
> Since I cannot physically see the `level.png` image, I will need to define a clickable zone for the "First Level" on the screen. By default, I will set this clickable zone to the top-left area or the center-left area of the screen (e.g., a rectangle roughly covering the first block). **Please let me know if the first level is located somewhere else on the image!**

> [!NOTE]
> I will change the actual game background from `level.png` to `back.png`. I will scale `back.png` to fill the 1080x720 window. Please confirm if this is the correct background image for the level.

## Proposed Changes

### `main.py`
- **Splash Screen Update:** Add `pygame.MOUSEBUTTONDOWN` event checking in the splash screen loop to exit the splash state.
- **Level Selection Loop [NEW]:**
  - Add a new `while` loop after the splash screen and before the main game loop.
  - Load `assets/level.png`, scale it to the window size, and draw it.
  - Create a `pygame.Rect` to represent the clickable area of Level 1 (e.g., `pygame.Rect(100, 100, 300, 300)`).
  - Handle `MOUSEBUTTONDOWN` events to check if the click coordinates fall within this `Rect`. If yes, exit the level selection loop and start the game.
- **Game Background Fix:**
  - Load `assets/back.png` instead of `assets/level.png` for the main `background` variable.
  - Scale it to `(1080, 720)` and draw it at `(0, 0)` instead of `(0, -200)`.

## Verification Plan
1. Launch `./env/bin/python3 main.py`.
2. Verify clicking the mouse advances the splash screen.
3. Verify `level.png` appears as the menu.
4. Verify clicking the "Level 1" area starts the game.
5. Verify `back.png` is the correct background during gameplay.
