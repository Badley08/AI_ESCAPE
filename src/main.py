import os
import sys
import json

# Résolution des chemins et modules compatible Windows & Linux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pygame
pygame.init()

from level1.core.game import Game as Game1
from level1.ui.hud import HUD as HUD1
from level2.core.game2 import Game2
from level3.core.game3 import Game3

# Fenêtre du jeu
pygame.display.set_caption("AI_ESCAPE")
app_icon = pygame.image.load('level1/assets/app_icon.png')
pygame.display.set_icon(app_icon)
screen = pygame.display.set_mode((1080, 720))

# Curseur personnalisé
pygame.mouse.set_visible(False)
pointer_image = pygame.image.load('level1/assets/pointer.png').convert_alpha()
pointer_image = pygame.transform.smoothscale(pointer_image, (44, 44))

# Polices de caractères pré-chargées
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

# -------------------------------------------------------------
# Assets Communs / Écrans
# -------------------------------------------------------------
splash_image = pygame.image.load('level1/assets/splash-screen.png').convert()
splash_image = pygame.transform.smoothscale(splash_image, (1080, 720))

level_map_image = pygame.image.load('level1/assets/level.png').convert()
level_map_image = pygame.transform.smoothscale(level_map_image, (720, 720))

level_1_rect = pygame.Rect(561, 404, 310, 281)  # Sector 1 : Test Alpha
level_2_rect = pygame.Rect(203, 276, 324, 290)  # Sector 2 : Test Beta
level_3_rect = pygame.Rect(521, 152, 175, 218)  # Sector 3 : Test Gamma

# Assets Level 1
l1_bg = pygame.image.load('level1/assets/background.png').convert()
l1_game_over_image = pygame.image.load('level1/assets/game_over.png').convert_alpha()
l1_game_over_image = pygame.transform.smoothscale(l1_game_over_image, (800, 250))
l1_victory_image = pygame.image.load('level1/assets/victory.png').convert_alpha()
l1_victory_image = pygame.transform.smoothscale(l1_victory_image, (800, 250))
l1_explosion_image = pygame.image.load('level1/assets/explosion.png').convert_alpha()
l1_explosion_image = pygame.transform.smoothscale(l1_explosion_image, (400, 400))

# Surfaces pré-allouées pour le verrouillage des secteurs
lock_overlay_surf_2 = pygame.Surface((level_2_rect.width, level_2_rect.height), pygame.SRCALPHA)
lock_overlay_surf_2.fill((20, 20, 30, 160))

lock_overlay_surf_3 = pygame.Surface((level_3_rect.width, level_3_rect.height), pygame.SRCALPHA)
lock_overlay_surf_3.fill((20, 20, 30, 160))

clock = pygame.time.Clock()

# -------------------------------------------------------------
# Système de Sauvegarde (sauvegarde.json)
# -------------------------------------------------------------
SAVE_FILE = 'sauvegarde.json'

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return {'unlocked_levels': [1], 'current_mode': 'splash', 'saved_battery': 100.0, 'level2_state': None, 'level3_state': None}

def save_game(unlocked_levels, current_mode, game2=None, game3=None, saved_battery=None):
    current_battery = saved_battery if saved_battery is not None else saved_progress.get('saved_battery', 100.0)
    save_data = {
        'unlocked_levels': list(unlocked_levels),
        'last_mode': current_mode,
        'saved_battery': current_battery,
        'level2_state': game2.get_save_state() if (game2 and current_mode == 'level2' and game2.state == 'playing') else None,
        'level3_state': game3.get_save_state() if (game3 and current_mode == 'level3' and game3.state == 'playing') else None
    }
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
    except Exception:
        pass

# Charger la sauvegarde existante
saved_progress = load_save()
unlocked_levels = set(saved_progress.get('unlocked_levels', [1]))

# -------------------------------------------------------------
# Gestionnaire Audio Centralisé
# -------------------------------------------------------------
current_music_file = None

def play_music(file_path, volume=0.7):
    global current_music_file
    if current_music_file == file_path and pygame.mixer.music.get_busy():
        return
    try:
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        current_music_file = file_path
    except Exception:
        pass

# Démarrer la musique du menu
play_music('level1/sounds/sleepless_corridor.mp3', 0.7)

current_mode = "splash"
locked_alert_timer = 0
locked_alert_msg = ""

game1 = None
hud1 = None
game2 = None
game3 = None

running = True

# =============================================================
# Boucle Principale Ultra-Optimisée
# =============================================================
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    # ---------------------------------------------------------
    # 1. Écran d'accueil (Splash Screen)
    # ---------------------------------------------------------
    if current_mode == "splash":
        play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
        screen.blit(splash_image, (0, 0))
        
        hint_text = font_small.render("CLICK OR PRESS SPACE TO START", True, (0, 220, 255))
        screen.blit(hint_text, hint_text.get_rect(centerx=540, y=675))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    current_mode = "level_select"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_mode = "level_select"

    # ---------------------------------------------------------
    # 2. Carte de Sélection des Niveaux (Station Spatiale)
    # ---------------------------------------------------------
    elif current_mode == "level_select":
        play_music('level1/sounds/sleepless_corridor.mp3', 0.7)

        screen.fill((10, 15, 25))
        screen.blit(level_map_image, (180, 0))

        title_surf = font_large.render("STATION ORBITALE - SÉLECTION DU SECTEUR", True, (0, 220, 255))
        screen.blit(title_surf, title_surf.get_rect(centerx=540, y=25))

        hover_l1 = level_1_rect.collidepoint(mouse_pos)
        hover_l2 = level_2_rect.collidepoint(mouse_pos)
        hover_l3 = level_3_rect.collidepoint(mouse_pos)

        # Secteur 1
        if hover_l1:
            pygame.draw.rect(screen, (0, 255, 150), level_1_rect, 3, border_radius=12)
            lbl = font_medium.render("SECTEUR 1 : TEST ALPHA (CLIQUEZ POUR ENTRER)", True, (0, 255, 150))
            screen.blit(lbl, lbl.get_rect(centerx=540, y=670))

        # Secteur 2 (Verrouillé ou Débloqué)
        if 2 not in unlocked_levels:
            screen.blit(lock_overlay_surf_2, level_2_rect.topleft)
            pygame.draw.rect(screen, (255, 60, 60), level_2_rect, 2, border_radius=12)
            badge = font_small.render("🔒 SECTEUR 2", True, (255, 80, 80))
            screen.blit(badge, badge.get_rect(center=level_2_rect.center))
            if hover_l2:
                lbl = font_medium.render("🔒 SECTEUR 2 BLOQUÉ : Complétez le Secteur 1 d'abord !", True, (255, 80, 80))
                screen.blit(lbl, lbl.get_rect(centerx=540, y=670))
        else:
            if hover_l2:
                pygame.draw.rect(screen, (0, 255, 255), level_2_rect, 3, border_radius=12)
                lbl = font_medium.render("SECTEUR 2 : TEST BETA (CLIQUEZ POUR ENTRER)", True, (0, 255, 255))
                screen.blit(lbl, lbl.get_rect(centerx=540, y=670))
            else:
                pygame.draw.rect(screen, (50, 200, 255), level_2_rect, 1, border_radius=12)

        # Secteur 3 (Verrouillé ou Débloqué)
        if 3 not in unlocked_levels:
            screen.blit(lock_overlay_surf_3, level_3_rect.topleft)
            pygame.draw.rect(screen, (255, 60, 60), level_3_rect, 2, border_radius=12)
            badge3 = font_small.render("🔒 SECTEUR 3", True, (255, 80, 80))
            screen.blit(badge3, badge3.get_rect(center=level_3_rect.center))
            if hover_l3:
                lbl = font_medium.render("🔒 SECTEUR 3 BLOQUÉ : Complétez le Secteur 2 d'abord !", True, (255, 80, 80))
                screen.blit(lbl, lbl.get_rect(centerx=540, y=670))
        else:
            if hover_l3:
                pygame.draw.rect(screen, (255, 100, 50), level_3_rect, 3, border_radius=12)
                lbl = font_medium.render("SECTEUR 3 : TEST GAMMA (CLIQUEZ POUR ENTRER)", True, (255, 120, 60))
                screen.blit(lbl, lbl.get_rect(centerx=540, y=670))
            else:
                pygame.draw.rect(screen, (220, 100, 50), level_3_rect, 1, border_radius=12)

        if locked_alert_timer > 0:
            locked_alert_timer -= 1
            alert_surf = font_medium.render(locked_alert_msg, True, (255, 50, 50))
            screen.blit(alert_surf, alert_surf.get_rect(centerx=540, y=640))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if level_1_rect.collidepoint(event.pos):
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    game1 = Game1()
                    hud1 = HUD1()
                    game1.start_ticks = pygame.time.get_ticks()
                    current_mode = "level1"
                elif level_2_rect.collidepoint(event.pos):
                    if 2 in unlocked_levels:
                        play_music('level2/sounds/protocol_evasion.mp3', 0.7)
                        saved_l2 = saved_progress.get('level2_state', None)
                        game2 = Game2(saved_data=saved_l2)
                        current_mode = "level2"
                    else:
                        locked_alert_msg = "Accès Refusé : Terminez le Secteur 1 pour déverrouiller le Secteur 2 !"
                        locked_alert_timer = 120
                elif level_3_rect.collidepoint(event.pos):
                    if 3 in unlocked_levels:
                        play_music('level3/sounds/Obsidian_Gate.mp3', 0.7)
                        game3 = Game3(saved_data=saved_progress)
                        current_mode = "level3"
                    else:
                        locked_alert_msg = "Accès Refusé : Terminez le Secteur 2 pour déverrouiller le Secteur 3 !"
                        locked_alert_timer = 120

    # ---------------------------------------------------------
    # 3. Gameplay NIVEAU 1 (Test Alpha)
    # ---------------------------------------------------------
    elif current_mode == "level1":
        screen.blit(l1_bg, (0, -200))

        if game1.state == "playing":
            screen.blit(game1.player.image, game1.player.rect)
            game1.canons.draw(screen)
            for canon in game1.canons:
                canon.all_projectiles.draw(screen)

            game1.update(hud1)
            hud1.draw(screen, game1.player, game1.get_seconds_left())

            if (game1.pressed.get(pygame.K_RIGHT) or game1.pressed.get(pygame.K_d)) and game1.player.rect.x < 980:
                game1.player.move_right()
            if (game1.pressed.get(pygame.K_LEFT) or game1.pressed.get(pygame.K_a)) and game1.player.rect.x > 0:
                game1.player.move_left()
            if (game1.pressed.get(pygame.K_UP) or game1.pressed.get(pygame.K_w)) and game1.player.rect.y > 420:
                game1.player.move_up()
            if (game1.pressed.get(pygame.K_DOWN) or game1.pressed.get(pygame.K_s)) and game1.player.rect.y < 584:
                game1.player.move_down()

        elif game1.state == "game_over":
            screen.blit(l1_explosion_image, (game1.player.rect.centerx - 200, game1.player.rect.centery - 200))
            game_over_rect = l1_game_over_image.get_rect(centerx=540, centery=360)
            screen.blit(l1_game_over_image, game_over_rect)

            restart_text = font_medium.render("Press R to restart | ESC for Sector Map", True, (0, 150, 255))
            screen.blit(restart_text, restart_text.get_rect(centerx=540, y=520))

        elif game1.state == "victory":
            unlocked_levels.add(2)
            save_game(unlocked_levels, "level_select")
            screen.blit(l1_victory_image, l1_victory_image.get_rect(centerx=540, centery=320))
            v_text1 = font_large.render("SECTEUR 2 DÉVERROUILLÉ !", True, (50, 255, 120))
            v_text2 = font_medium.render("Appuyez sur ESPACE pour passer à la Station et au Niveau 2", True, (0, 220, 255))
            screen.blit(v_text1, v_text1.get_rect(centerx=540, centery=430))
            screen.blit(v_text2, v_text2.get_rect(centerx=540, centery=480))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game1.pressed[event.key] = True
                if event.key == pygame.K_ESCAPE:
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    current_mode = "level_select"
                elif event.key == pygame.K_r and game1.state in ("game_over", "victory"):
                    game1 = Game1()
                    hud1 = HUD1()
                    game1.start_ticks = pygame.time.get_ticks()
                elif event.key == pygame.K_SPACE and game1.state == "victory":
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    current_mode = "level_select"
            elif event.type == pygame.KEYUP:
                game1.pressed[event.key] = False

    # ---------------------------------------------------------
    # 4. Gameplay NIVEAU 2 (Test Beta)
    # ---------------------------------------------------------
    elif current_mode == "level2":
        game2.update()
        game2.render(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game2.pressed[event.key] = True
                if event.key == pygame.K_ESCAPE:
                    game2.stop_all_sounds()
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    save_game(unlocked_levels, "level2", game2=game2)
                    current_mode = "level_select"
                elif event.key == pygame.K_r and game2.state in ("game_over", "victory"):
                    game2.stop_all_sounds()
                    play_music('level2/sounds/protocol_evasion.mp3', 0.7)
                    game2 = Game2()
                elif event.key == pygame.K_SPACE and game2.state == "victory":
                    game2.stop_all_sounds()
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    unlocked_levels.add(3)
                    save_game(unlocked_levels, "level_select", saved_battery=game2.final_transferred_battery)
                    current_mode = "level_select"
            elif event.type == pygame.KEYUP:
                game2.pressed[event.key] = False

    # ---------------------------------------------------------
    # 5. Gameplay NIVEAU 3 (Test Gamma)
    # ---------------------------------------------------------
    elif current_mode == "level3":
        game3.update()
        game3.render(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game3.pressed[event.key] = True
                if event.key == pygame.K_ESCAPE:
                    game3.stop_all_sounds()
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    save_game(unlocked_levels, "level3", game3=game3)
                    current_mode = "level_select"
                elif event.key == pygame.K_r and game3.state in ("game_over", "victory"):
                    game3.stop_all_sounds()
                    play_music('level3/sounds/Obsidian_Gate.mp3', 0.7)
                    game3 = Game3(saved_data=saved_progress)
                elif event.key == pygame.K_SPACE and game3.state == "victory":
                    game3.stop_all_sounds()
                    play_music('level1/sounds/sleepless_corridor.mp3', 0.7)
                    unlocked_levels.add(4)
                    save_game(unlocked_levels, "level_select", saved_battery=game3.final_transferred_battery)
                    current_mode = "level_select"
            elif event.type == pygame.KEYUP:
                game3.pressed[event.key] = False

    # Curseur Personnalisé
    screen.blit(pointer_image, mouse_pos)
    pygame.display.flip()

# Sauvegarde automatique à la fermeture
save_game(unlocked_levels, current_mode, game2=game2, game3=game3)
pygame.quit()
