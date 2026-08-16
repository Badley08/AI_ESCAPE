import math
import random
import pygame
from level3.core.tilemap3 import TileMap3
from level3.entities.player3 import Player3
from level3.entities.enemy import EnemyRobot
from level3.entities.projectile import Projectile
from level3.entities.terminal import Terminal
from level3.entities.explosion3 import Explosion3
from level3.ui.hud3 import HUD3


class Game3:
    """Gestionnaire principal du Niveau 3 (TEST GAMMA) — 6 Générateurs, Gardes & Furtivité/Combat."""

    MAX_WAVES = 3
    WAVE_ENEMIES = [3, 4, 5]

    def __init__(self, saved_data=None):
        # 1. Carte de l'arène
        self.tilemap = TileMap3('level3/assets/level3_grid.json')
        self.bg_image = pygame.image.load('level3/assets/level3_background.png').convert()
        self.bg_image = pygame.transform.smoothscale(
            self.bg_image, (self.tilemap.map_width, self.tilemap.map_height))

        # 2. Joueur (spawn dans le sas sud, à l'intérieur de l'arène)
        spawn_x = 840.0
        spawn_y = 744.0
        self.player = Player3(spawn_x, spawn_y, self.tilemap)

        if saved_data and 'saved_battery' in saved_data:
            self.player.battery = float(saved_data['saved_battery'])
        elif saved_data and 'player_battery' in saved_data:
            self.player.battery = float(saved_data['player_battery'])

        # 3. Groupes de sprites
        self.enemies = pygame.sprite.Group()
        self.player_projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        # 4. Les 6 Terminaux répartis dans l'arène
        self.terminals = [
            Terminal(328, 200, 1),   # Nord-Ouest
            Terminal(1304, 248, 2),  # Nord-Est
            Terminal(376, 472, 3),   # Ouest-Centre
            Terminal(1288, 472, 4),  # Est-Centre
            Terminal(344, 728, 5),   # Sud-Ouest
            Terminal(1272, 696, 6),  # Sud-Est
        ]

        # 5. Système de vagues et d'apparition
        self.current_wave = 0
        self.wave_active = False
        self.wave_delay = 90
        self.all_waves_complete = False
        self._enemy_spawn_points = self._find_spawn_points()

        # Initialiser 2 gardes noirs près des terminaux nord
        self.enemies.add(EnemyRobot(340, 260, 1, self.tilemap, guard_terminal=self.terminals[0]))
        self.enemies.add(EnemyRobot(1280, 290, 1, self.tilemap, guard_terminal=self.terminals[1]))

        # 6. Interface
        self.hud = HUD3()
        self.pressed = {}
        self.state = "playing"
        self.mouse_pos = (540, 360)

        self.battery_bonus_awarded = 0.0
        self.final_transferred_battery = 100.0

        # 7. Porte de sortie (haut centre)
        self.exit_rect = pygame.Rect(812, 170, 56, 56)
        self.exit_open = False

        # 8. Overlays & Polices
        self.game_over_overlay = pygame.Surface((1080, 720), pygame.SRCALPHA)
        self.game_over_overlay.fill((0, 0, 0, 185))
        self.victory_overlay = pygame.Surface((1080, 720), pygame.SRCALPHA)
        self.victory_overlay.fill((5, 20, 40, 185))

        self.font_large = pygame.font.Font(None, 56)
        self.font_med = pygame.font.Font(None, 30)

        # 9. Audio
        try:
            self.snd_player_laser = pygame.mixer.Sound('level3/sounds/laser_player.mp3')
            self.snd_player_laser.set_volume(0.5)
            self.snd_enemy_laser = pygame.mixer.Sound('level3/sounds/laser_enemy.mp3')
            self.snd_enemy_laser.set_volume(0.35)
            self.snd_robot_destroyed = pygame.mixer.Sound('level3/sounds/robot_destroyed.mp3')
            self.snd_robot_destroyed.set_volume(0.8)
            self.snd_terminal = pygame.mixer.Sound('level3/sounds/terminal_activated.mp3')
            self.snd_terminal.set_volume(0.9)
        except Exception:
            self.snd_player_laser = None
            self.snd_enemy_laser = None
            self.snd_robot_destroyed = None
            self.snd_terminal = None

    def _find_spawn_points(self):
        points = []
        ts = self.tilemap.tile_size
        for r in range(4, self.tilemap.rows - 4, 3):
            for c in range(4, self.tilemap.cols - 4, 3):
                px = c * ts + ts // 2
                py = r * ts + ts // 2
                if self.tilemap.is_walkable(px, py):
                    clear = all(
                        self.tilemap.is_walkable(px + dx * ts, py + dy * ts)
                        for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    )
                    if clear:
                        points.append((px, py))
        return points

    def _spawn_wave(self):
        if self.current_wave >= self.MAX_WAVES:
            self.all_waves_complete = True
            return

        count = self.WAVE_ENEMIES[self.current_wave]
        far_points = [p for p in self._enemy_spawn_points
                      if math.hypot(p[0] - self.player.pos_x, p[1] - self.player.pos_y) > 320]
        if len(far_points) < count:
            far_points = self._enemy_spawn_points[:]

        random.shuffle(far_points)
        for i in range(min(count, len(far_points))):
            variant = (i % 3) + 1  # 1 = Garde noir, 2 & 3 = Patrouilleurs
            ex, ey = far_points[i]
            self.enemies.add(EnemyRobot(ex, ey, variant, self.tilemap))

        self.current_wave += 1
        self.wave_active = True

    def get_save_state(self):
        return {
            'player_battery': round(self.player.battery, 1),
            'current_wave': self.current_wave,
        }

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def update(self):
        if self.state != "playing":
            return

        # Caméra
        cam_x = max(0, min(self.tilemap.map_width - 1080, int(self.player.pos_x - 540)))
        cam_y = max(0, min(self.tilemap.map_height - 720, int(self.player.pos_y - 360)))

        mx, my = pygame.mouse.get_pos()
        self.mouse_pos = (mx, my)
        world_mx = mx + cam_x
        world_my = my + cam_y

        # Joueur
        self.player.move(self.pressed)
        self.player.update_aim(world_mx, world_my)
        self.player.update()

        # Tir du joueur : Clic Gauche OU Touche ESPACE
        mouse_buttons = pygame.mouse.get_pressed()
        space_pressed = self.pressed.get(pygame.K_SPACE, False)
        if (mouse_buttons[0] or space_pressed) and self.player.try_shoot():
            angle = self.player.fire_angle
            proj = Projectile(self.player.pos_x, self.player.pos_y, angle, True, self.tilemap)
            self.player_projectiles.add(proj)
            if self.snd_player_laser:
                self.snd_player_laser.play()

        # Système de vagues
        if not self.wave_active and not self.all_waves_complete:
            self.wave_delay -= 1
            if self.wave_delay <= 0:
                self._spawn_wave()
                self.wave_delay = 180

        if self.wave_active and len(self.enemies) == 0:
            self.wave_active = False
            self.wave_delay = 180

        # Ennemis synchronisés
        EnemyRobot.tick_global_clock()
        for e in list(self.enemies):
            e.update(self.player, self.enemy_projectiles, self.snd_enemy_laser)

        self.player_projectiles.update()
        self.enemy_projectiles.update()
        self.explosions.update()

        # Collision lasers joueur → ennemis
        for proj in list(self.player_projectiles):
            for enemy in list(self.enemies):
                if proj.rect.colliderect(enemy.hitbox):
                    proj.kill()
                    if enemy.take_hit():
                        self.explosions.add(Explosion3(enemy.pos_x, enemy.pos_y))
                        enemy.kill()
                        self.player.restore_battery(4.0)
                        if self.snd_robot_destroyed:
                            self.snd_robot_destroyed.play()
                    break

        # Collision lasers ennemis → joueur
        player_hit_rect = pygame.Rect(0, 0, 18, 18)
        player_hit_rect.center = (round(self.player.pos_x), round(self.player.pos_y))
        for proj in list(self.enemy_projectiles):
            if proj.rect.colliderect(player_hit_rect):
                proj.kill()
                self.player.take_damage(4.5)

        # Terminaux : activation touche E & alerte des gardes
        holding_e = self.pressed.get(pygame.K_e, False)
        for t in self.terminals:
            t.update()
            just_activated = t.try_activate(self.player.pos_x, self.player.pos_y, holding_e)
            if just_activated:
                self.player.restore_battery(12.0)
                if self.snd_terminal:
                    self.snd_terminal.play()

                # Le garde le plus proche est alerté et part inspecter le terminal piraté
                closest_guard = None
                min_guard_dist = 99999
                for e in self.enemies:
                    if e.is_guard:
                        d = math.hypot(e.pos_x - t.x, e.pos_y - t.y)
                        if d < min_guard_dist:
                            min_guard_dist = d
                            closest_guard = e

                if closest_guard:
                    closest_guard.alert_to_terminal((t.x, t.y))

        # Condition de victoire : Les 6 terminaux activés (permet victoire Pacifiste/Furtive OU Combat)
        terminals_done = sum(1 for t in self.terminals if t.activated)
        if terminals_done >= len(self.terminals):
            self.exit_open = True

        # Défaite
        if self.player.battery <= 0:
            self.state = "game_over"
            self.stop_all_sounds()
            return

        # Victoire
        if self.exit_open and self.player.hitbox.colliderect(self.exit_rect):
            self.state = "victory"
            self.stop_all_sounds()
            perf = min(1.0, self.player.battery / 100.0)
            self.battery_bonus_awarded = round(20.0 + perf * 20.0, 1)
            self.final_transferred_battery = min(100.0, round(self.player.battery + self.battery_bonus_awarded, 1))
            return

    def render(self, screen):
        cam_x = max(0, min(self.tilemap.map_width - 1080, int(self.player.pos_x - 540)))
        cam_y = max(0, min(self.tilemap.map_height - 720, int(self.player.pos_y - 360)))
        off_x = -cam_x
        off_y = -cam_y

        screen.fill((5, 5, 10))
        screen.blit(self.bg_image, (off_x, off_y))

        # Terminaux
        for t in self.terminals:
            t.draw(screen, off_x, off_y)

        # Porte de sortie
        door_pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
        door_color = (0, 255, 120) if self.exit_open else (255, 50, 50)
        dsx = self.exit_rect.centerx + off_x
        dsy = self.exit_rect.centery + off_y
        pygame.draw.circle(screen, door_color, (dsx, dsy), int(20 + door_pulse * 4), 3)
        if self.exit_open:
            pygame.draw.circle(screen, (50, 255, 150), (dsx, dsy), 16)

        # Explosions
        for exp in self.explosions:
            screen.blit(exp.image, (exp.rect.x + off_x, exp.rect.y + off_y))

        # Ennemis
        for e in self.enemies:
            screen.blit(e.image, (e.rect.x + off_x, e.rect.y + off_y))
            if e.hp < e.max_hp:
                bar_w = 30
                bx = round(e.pos_x) + off_x - bar_w // 2
                by = round(e.pos_y) + off_y - 30
                pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, 4))
                fill = int(bar_w * e.hp / e.max_hp)
                pygame.draw.rect(screen, (255, 50, 50), (bx, by, fill, 4))

        # Projectiles
        for p in self.player_projectiles:
            screen.blit(p.image, (p.rect.x + off_x, p.rect.y + off_y))
        for p in self.enemy_projectiles:
            screen.blit(p.image, (p.rect.x + off_x, p.rect.y + off_y))

        # Joueur
        screen.blit(self.player.image, (self.player.rect.x + off_x, self.player.rect.y + off_y))

        # HUD
        terminals_done = sum(1 for t in self.terminals if t.activated)
        self.hud.draw(
            screen, self.player,
            self.current_wave, self.MAX_WAVES,
            len(self.enemies), terminals_done, len(self.terminals),
            self.mouse_pos
        )

        if self.state == "game_over":
            screen.blit(self.game_over_overlay, (0, 0))
            t1 = self.font_large.render("SYSTÈME CRITIQUE : DÉTRUIT", True, (255, 50, 50))
            t2 = self.font_med.render("Appuyez sur R pour Recommencer | ECHAP pour la Station", True, (0, 200, 255))
            screen.blit(t1, t1.get_rect(centerx=540, centery=320))
            screen.blit(t2, t2.get_rect(centerx=540, centery=400))
        elif self.state == "victory":
            screen.blit(self.victory_overlay, (0, 0))
            t1 = self.font_large.render("TEST GAMMA ACCOMPLI !", True, (50, 255, 120))
            t2 = self.font_med.render(f"Batterie: {int(self.player.battery)}%  |  Bonus: +{int(self.battery_bonus_awarded)}%", True, (255, 255, 255))
            t3 = self.font_med.render(f"Batterie transmise: {int(self.final_transferred_battery)}%", True, (0, 220, 255))
            t4 = self.font_med.render("Appuyez sur ENTRÉE pour revenir à la Station", True, (50, 255, 120))
            screen.blit(t1, t1.get_rect(centerx=540, centery=270))
            screen.blit(t2, t2.get_rect(centerx=540, centery=330))
            screen.blit(t3, t3.get_rect(centerx=540, centery=380))
            screen.blit(t4, t4.get_rect(centerx=540, centery=450))
