import math
import pygame
from Station_Sector1.level2.core.tilemap import TileMap
from Station_Sector1.level2.entities.player2 import Player2
from Station_Sector1.level2.entities.cleaner import CleanerRobot
from Station_Sector1.level2.entities.fragment import DataBox
from Station_Sector1.level2.entities.reactor import Reactor
from Station_Sector1.level2.ui.hud2 import HUD2

class Game2:
    """Gestionnaire principal du Niveau 2 avec calcul de bonus de batterie et rotation fluide."""

    def __init__(self, saved_data=None):
        # 1. Carte & Grille
        self.tilemap = TileMap('Station_Sector1/level2/level2_grid.json')
        self.bg_image = pygame.image.load('Station_Sector1/level2/level2_background.png').convert()

        # 2. Joueur (Départ en bas au centre en zone dégagée)
        start_x = saved_data.get('player_x', 520) if saved_data else 520
        start_y = saved_data.get('player_y', 936) if saved_data else 936
        self.player = Player2(start_x, start_y, self.tilemap)
        
        # Le niveau 2 commence à 100% (ou reprend la sauvegarde en cours de niveau 2)
        if saved_data and 'player_battery' in saved_data:
            self.player.battery = float(saved_data['player_battery'])
        else:
            self.player.battery = 100.0

        if saved_data and 'carried_cores' in saved_data:
            self.player.carried_cores = int(saved_data['carried_cores'])

        # 3. Véhicule Nettoyeur
        cleaner_x = saved_data.get('cleaner_x', 820) if saved_data else 820
        cleaner_y = saved_data.get('cleaner_y', 150) if saved_data else 150
        self.cleaner = CleanerRobot(cleaner_x, cleaner_y, self.tilemap)

        # 4. Les 2 Réacteurs
        self.reactor_center = Reactor("RÉACTEUR CENTRAL", 500, 520, max_cores=3)
        self.reactor_right = Reactor("RÉACTEUR DROIT", 850, 520, max_cores=3)
        if saved_data:
            self.reactor_center.cores = saved_data.get('reactor_center_cores', 0)
            self.reactor_center._update_text()
            self.reactor_right.cores = saved_data.get('reactor_right_cores', 0)
            self.reactor_right._update_text()

        # 5. Emplacements des 6 boîtes
        all_box_coords = [
            (232, 104),   # Salle Nord-Ouest
            (808, 240),   # Salle Nord-Est
            (152, 360),   # Salle Centre-Ouest
            (136, 600),   # Salle Sud-Ouest
            (760, 776),   # Salle Sud-Est
            (248, 856)    # Salle Sud-Centre
        ]
        
        saved_remaining_boxes = saved_data.get('remaining_boxes', None) if saved_data else None
        self.boxes = pygame.sprite.Group()
        if saved_remaining_boxes is not None:
            for x, y in saved_remaining_boxes:
                self.boxes.add(DataBox(x, y))
        else:
            for x, y in all_box_coords:
                self.boxes.add(DataBox(x, y))

        self.exit_open = (self.reactor_center.is_full and self.reactor_right.is_full)
        self.exit_sound_played = self.exit_open
        self.exit_rect = pygame.Rect(492, 40, 40, 40)

        # 6. Interface & Récompense de performance
        self.hud = HUD2()
        self.pressed = {}
        self.state = "playing"
        self.battery_bonus_awarded = 0
        self.final_transferred_battery = 100.0

        self.game_over_overlay = pygame.Surface((1080, 720), pygame.SRCALPHA)
        self.game_over_overlay.fill((0, 0, 0, 185))
        self.victory_overlay = pygame.Surface((1080, 720), pygame.SRCALPHA)
        self.victory_overlay.fill((5, 20, 40, 185))

        self.font_large = pygame.font.Font(None, 56)
        self.font_med = pygame.font.Font(None, 30)

        # 7. Audio
        try:
            self.sound_collect = pygame.mixer.Sound('Station_Sector1/level2/sounds/data_collect.mp3')
            self.sound_collect.set_volume(0.8)
            self.sound_crushed = pygame.mixer.Sound('Station_Sector1/level2/sounds/robot_crushed.mp3')
            self.sound_crushed.set_volume(0.9)
            self.sound_teleport = pygame.mixer.Sound('Station_Sector1/level2/sounds/teleport.mp3')
            self.sound_teleport.set_volume(0.9)
        except Exception:
            self.sound_collect = None
            self.sound_crushed = None
            self.sound_teleport = None

    def get_save_state(self):
        remaining_boxes = [(int(b.base_x), int(b.base_y)) for b in self.boxes]
        return {
            'player_x': int(self.player.pos_x),
            'player_y': int(self.player.pos_y),
            'player_battery': round(self.player.battery, 1),
            'carried_cores': self.player.carried_cores,
            'cleaner_x': int(self.cleaner.pos_x),
            'cleaner_y': int(self.cleaner.pos_y),
            'reactor_center_cores': self.reactor_center.cores,
            'reactor_right_cores': self.reactor_right.cores,
            'remaining_boxes': remaining_boxes
        }

    def stop_all_sounds(self):
        self.cleaner.stop_sound()
        pygame.mixer.stop()

    def update(self):
        if self.state != "playing":
            return

        self.player.move(self.pressed)
        self.player.update()
        self.boxes.update()
        self.cleaner.update(self.player)

        # Ramassage d'une boîte
        if self.player.carried_cores == 0:
            collected = pygame.sprite.spritecollide(
                self.player,
                self.boxes,
                True,
                pygame.sprite.collide_circle_ratio(0.85)
            )
            for _ in collected:
                self.player.carried_cores += 1
                if self.sound_collect:
                    self.sound_collect.play()

        # Dépôt dans réacteur
        if self.player.carried_cores > 0:
            p_center = (self.player.pos_x, self.player.pos_y)
            
            dist_c = math.hypot(p_center[0] - self.reactor_center.x, p_center[1] - self.reactor_center.y)
            if dist_c < self.reactor_center.radius + 15 and not self.reactor_center.is_full:
                if self.reactor_center.deposit_core():
                    self.player.carried_cores -= 1
                    self.player.restore_battery(15.0)
                    self.hud.trigger_deposit_flash()
                    if self.sound_collect:
                        self.sound_collect.play()

            dist_r = math.hypot(p_center[0] - self.reactor_right.x, p_center[1] - self.reactor_right.y)
            if dist_r < self.reactor_right.radius + 15 and not self.reactor_right.is_full and self.player.carried_cores > 0:
                if self.reactor_right.deposit_core():
                    self.player.carried_cores -= 1
                    self.player.restore_battery(15.0)
                    self.hud.trigger_deposit_flash()
                    if self.sound_collect:
                        self.sound_collect.play()

        # Ouverture porte
        if self.reactor_center.is_full and self.reactor_right.is_full and not self.exit_open:
            self.exit_open = True
            if not self.exit_sound_played and self.sound_teleport:
                self.sound_teleport.play()
                self.exit_sound_played = True

        # Défaite
        if self.player.hitbox.colliderect(self.cleaner.attack_hitbox) or self.player.battery <= 0:
            self.state = "game_over"
            self.stop_all_sounds()
            if self.sound_crushed:
                self.sound_crushed.play()
            return

        # Victoire : calcul de la récompense selon la performance (jamais plus de 50%)
        if self.exit_open and self.player.hitbox.colliderect(self.exit_rect):
            self.state = "victory"
            self.stop_all_sounds()
            
            # Bonus de performance : 20% de base + jusqu'à 20% selon la batterie restante (max 40% < 50%)
            perf_factor = min(1.0, self.player.battery / 100.0)
            self.battery_bonus_awarded = round(20.0 + perf_factor * 20.0, 1)  # Ex: +35%
            # La batterie transmise aux niveaux suivants = batterie restante + bonus (plafonné à 100%)
            self.final_transferred_battery = min(100.0, round(self.player.battery + self.battery_bonus_awarded, 1))

            if self.sound_teleport:
                self.sound_teleport.play()
            return

    def render(self, screen):
        offset_x = (1080 - 1024) // 2
        cam_y = max(0, min(1024 - 720, int(self.player.pos_y - 360)))

        screen.fill((8, 12, 20))
        screen.blit(self.bg_image, (offset_x, -cam_y))

        self.reactor_center.draw(screen, offset_x, -cam_y)
        self.reactor_right.draw(screen, offset_x, -cam_y)

        door_pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
        door_color = (0, 255, 120) if self.exit_open else (255, 50, 50)
        door_screen_x = self.exit_rect.centerx + offset_x
        door_screen_y = self.exit_rect.centery - cam_y
        
        pygame.draw.circle(screen, door_color, (door_screen_x, door_screen_y), int(18 + door_pulse * 4), 3)
        if self.exit_open:
            pygame.draw.circle(screen, (50, 255, 150, 100), (door_screen_x, door_screen_y), 16)

        for b in self.boxes:
            screen.blit(b.image, (b.rect.x + offset_x, b.rect.y - cam_y))

        screen.blit(self.cleaner.image, (self.cleaner.rect.x + offset_x, self.cleaner.rect.y - cam_y))
        screen.blit(self.player.image, (self.player.rect.x + offset_x, self.player.rect.y - cam_y))
        self.player.draw_carried_indicator(screen, offset_x, -cam_y)

        dist_to_cleaner = math.hypot(
            self.player.pos_x - self.cleaner.pos_x,
            self.player.pos_y - self.cleaner.pos_y
        )
        self.hud.draw(
            screen,
            self.player,
            self.reactor_center,
            self.reactor_right,
            self.exit_open,
            dist_to_cleaner
        )

        if self.state == "game_over":
            screen.blit(self.game_over_overlay, (0, 0))
            t1 = self.font_large.render("SYSTÈME CRITIQUE : DÉTRUIT", True, (255, 50, 50))
            t2 = self.font_med.render("Appuyez sur R pour Recommencer | ECHAP pour la Station", True, (0, 200, 255))
            screen.blit(t1, t1.get_rect(centerx=540, centery=320))
            screen.blit(t2, t2.get_rect(centerx=540, centery=400))
        elif self.state == "victory":
            screen.blit(self.victory_overlay, (0, 0))
            t1 = self.font_large.render("TEST BÊTA ACCOMPLI !", True, (50, 255, 120))
            t2 = self.font_med.render(f"Batterie restante: {int(self.player.battery)}%  |  Bonus Performance: +{int(self.battery_bonus_awarded)}%", True, (255, 255, 255))
            t3 = self.font_med.render(f"Batterie transmise au Niveau Suivant: {int(self.final_transferred_battery)}%", True, (0, 220, 255))
            t4 = self.font_med.render("Appuyez sur ESPACE pour revenir à la Station", True, (50, 255, 120))
            
            screen.blit(t1, t1.get_rect(centerx=540, centery=270))
            screen.blit(t2, t2.get_rect(centerx=540, centery=330))
            screen.blit(t3, t3.get_rect(centerx=540, centery=380))
            screen.blit(t4, t4.get_rect(centerx=540, centery=450))
