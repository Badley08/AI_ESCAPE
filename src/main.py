import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
from level1.core.game import Game
from level1.ui.hud import HUD
pygame.init()


#Game window
pygame.display.set_caption("AI_ESCAPE")
app_icon = pygame.image.load('level1/assets/app_icon.png')
pygame.display.set_icon(app_icon)
screen = pygame.display.set_mode((1080, 720))

#Background
background = pygame.image.load('level1/assets/background.png')

#Load the game over and victory images
game_over_image = pygame.image.load('level1/assets/game_over.png')
game_over_image = pygame.transform.smoothscale(game_over_image, (800, 250))
victory_image = pygame.image.load('level1/assets/victory.png')
victory_image = pygame.transform.smoothscale(victory_image, (800, 250))
#Load the explosion image for game over screen
explosion_image = pygame.image.load('level1/assets/explosion.png')
explosion_image = pygame.transform.smoothscale(explosion_image, (400, 400))

#load our player
game = Game()

#Create the HUD
hud = HUD()

#Clock for FPS cap
clock = pygame.time.Clock()

# Hide default cursor and load custom pointer
pygame.mouse.set_visible(False)
pointer_image = pygame.image.load('level1/assets/pointer.png')
# Since it is large (755KB), scale it down to a typical cursor size
pointer_image = pygame.transform.smoothscale(pointer_image, (48, 48))

running = True

# Splash Screen logic
splash_image = pygame.image.load('level1/assets/splash-screen.png')
splash_image = pygame.transform.smoothscale(splash_image, (1080, 720))

pygame.mixer.music.load('level1/sounds/sleepless_corridor.mp3')
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)

showing_splash = True
while showing_splash and running:
    clock.tick(60)
    
    # Loop music exactly at 26 seconds (26000 ms) to avoid gap
    if pygame.mixer.music.get_pos() >= 26000:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1.0)
        
    screen.blit(splash_image, (0, 0))
    
    # Draw custom pointer
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(pointer_image, mouse_pos)
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            showing_splash = False
            running = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                showing_splash = False
            elif event.key == pygame.K_ESCAPE:
                showing_splash = False
                running = False
                pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                showing_splash = False

# Level Selection logic
level_image = pygame.image.load('level1/assets/level.png')
level_image = pygame.transform.smoothscale(level_image, (720, 720))
level_1_rect = pygame.Rect(561, 404, 310, 281)

selecting_level = True
while selecting_level and running:
    clock.tick(60)
    
    if pygame.mixer.music.get_pos() >= 26000:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(1.0)
        
    screen.fill((0, 0, 0))
    screen.blit(level_image, (180, 0))
    
    # Draw custom pointer
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(pointer_image, mouse_pos)
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            selecting_level = False
            running = False
            pygame.quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            selecting_level = False
            running = False
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if level_1_rect.collidepoint(event.pos):
                    selecting_level = False
                    pygame.mixer.music.set_volume(0.7)

if running:
    # Reset timer because time elapsed during the splash screen
    game.start_ticks = pygame.time.get_ticks()

#Game loop
while running:

    #Cap the framerate at 60 FPS
    clock.tick(60)

    # Loop music exactly at 26 seconds (26000 ms) to avoid gap
    if pygame.mixer.music.get_pos() >= 26000:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)

    #Draw the background
    screen.blit(background, (0,-200))

    #If the game is still playing
    if game.state == "playing":

        #Add the player image on the screen
        screen.blit(game.player.image, game.player.rect)

        #Draw all canons
        game.canons.draw(screen)
        
        # Draw projectiles
        for canon in game.canons:
            canon.all_projectiles.draw(screen)

        #Update the game logic (collisions, timer, shooting)
        game.update(hud)

        #Draw the HUD (health bar, timer, intro text, damage flash)
        hud.draw(screen, game.player, game.get_seconds_left())

    #If the game is over (player died)
    elif game.state == "game_over":
        #Draw the explosion at the player position
        screen.blit(explosion_image, (game.player.rect.centerx - 200, game.player.rect.centery - 200))
        #Draw the game over image centered on screen
        game_over_rect = game_over_image.get_rect(centerx=540, centery=360)
        screen.blit(game_over_image, game_over_rect)
        #Draw the restart instruction
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Press R to restart or ESC to quit", True, (0, 150, 255))
        restart_rect = restart_text.get_rect(centerx=540, y=520)
        screen.blit(restart_text, restart_rect)

    #If the player survived 60 seconds (victory)
    elif game.state == "victory":
        #Draw the victory image centered on screen
        victory_rect = victory_image.get_rect(centerx=540, centery=360)
        screen.blit(victory_image, victory_rect)
        #Draw the restart instruction
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Press R to restart or ESC to quit", True, (0, 150, 255))
        restart_rect = restart_text.get_rect(centerx=540, y=520)
        screen.blit(restart_text, restart_rect)

    # Draw the custom pointer
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(pointer_image, mouse_pos)

    #Update the display
    pygame.display.flip()

    #If the player closes the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Quitting the game")
        #Define that the pressed keys are true
        elif event.type == pygame.KEYDOWN:
            game.pressed[event.key] = True

            #If the player presses ESC, quit the game
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()

            #If the player presses R during game over or victory, restart
            if event.key == pygame.K_r and game.state in ("game_over", "victory"):
                game = Game()
                hud = HUD()

        #Define that the released keys are false
        elif event.type == pygame.KEYUP:
            game.pressed[event.key] = False

    if running and game.state == "playing":
        #Verify if the player wants to move
        if (game.pressed.get(pygame.K_RIGHT) or game.pressed.get(pygame.K_d)) and game.player.rect.x < 980:
            game.player.move_right()
        if (game.pressed.get(pygame.K_LEFT) or game.pressed.get(pygame.K_a)) and game.player.rect.x > 0:
            game.player.move_left()
        if (game.pressed.get(pygame.K_UP) or game.pressed.get(pygame.K_w)) and game.player.rect.y > 420:
            game.player.move_up()
        if (game.pressed.get(pygame.K_DOWN) or game.pressed.get(pygame.K_s)) and game.player.rect.y < 584:
            game.player.move_down()
