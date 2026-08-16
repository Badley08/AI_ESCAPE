import math
import random
import pygame
from level3.entities.projectile import Projectile


class EnemyRobot(pygame.sprite.Sprite):
    """Robot ennemi corrompu — IA tactique : chasse, se met à couvert et tire en salve double."""

    SPEED = 2.0
    DETECTION_RANGE = 300
    COVER_RANGE = 120       # Distance idéale de tir (derrière un abri)
    FIRE_INTERVAL = 90      # Intervalle de tir synchronisé (~1.5 sec à 60 FPS)

    # Compteur global partagé pour synchroniser les salves de tous les ennemis
    _global_fire_clock = 0

    @classmethod
    def tick_global_clock(cls):
        """Appelé une fois par frame dans game3.update() pour synchroniser les tirs."""
        cls._global_fire_clock += 1

    @classmethod
    def reset_global_clock(cls):
        cls._global_fire_clock = 0

    def __init__(self, x, y, variant, tilemap):
        super().__init__()
        self.tilemap = tilemap
        self.variant = variant

        # Sprite selon la variante
        sprite_files = {1: 'enemy_robot.png', 2: 'enemy_robot2.png', 3: 'enemy_robot3.png'}
        raw = pygame.image.load(f'level3/assets/{sprite_files.get(variant, "enemy_robot.png")}').convert_alpha()
        ratio = raw.get_width() / raw.get_height()
        size_h = 44 + variant * 4
        self.base_image = pygame.transform.smoothscale(raw, (int(size_h * ratio), size_h))
        self.image = self.base_image

        self.pos_x = float(x)
        self.pos_y = float(y)
        self.hitbox = pygame.Rect(0, 0, 16, 16)
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Stats
        self.max_hp = variant + 1  # 2, 3, 4 HP
        self.hp = self.max_hp
        self.angle = 0.0

        # IA tactique
        self.state = 'patrol'  # 'patrol', 'chase', 'cover_seek', 'cover_fire'
        self.patrol_dir_x = random.choice([-1, 0, 1])
        self.patrol_dir_y = random.choice([-1, 0, 1])
        self.patrol_timer = random.randint(60, 180)
        self.cover_pos = None
        self.cover_timer = 0
        self.has_line_of_sight = False

    def _check_los(self, target_x, target_y):
        """Vérifie la ligne de vue vers la cible (raycast simple par pas de 16px)."""
        dx = target_x - self.pos_x
        dy = target_y - self.pos_y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return True
        steps = int(dist / 16) + 1
        sx = dx / steps
        sy = dy / steps
        for i in range(1, steps):
            px = self.pos_x + sx * i
            py = self.pos_y + sy * i
            if not self.tilemap.is_walkable(px, py):
                return False
        return True

    def _find_cover_near(self, player_x, player_y):
        """Trouve une position de couverture : praticable, proche d'un mur, avec LOS vers le joueur."""
        best = None
        best_score = -999
        ts = self.tilemap.tile_size
        search_r = 8  # rayon de recherche en tiles

        cx = int(self.pos_x) // ts
        cy = int(self.pos_y) // ts

        for dr in range(-search_r, search_r + 1, 2):
            for dc in range(-search_r, search_r + 1, 2):
                nc, nr = cx + dc, cy + dr
                if 0 <= nc < self.tilemap.cols and 0 <= nr < self.tilemap.rows:
                    if not self.tilemap.grid[nr][nc]:
                        continue
                    # Vérifier qu'il y a un mur adjacent (couverture)
                    has_wall_nearby = False
                    for wd in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        wc, wr = nc + wd[0], nr + wd[1]
                        if 0 <= wc < self.tilemap.cols and 0 <= wr < self.tilemap.rows:
                            if not self.tilemap.grid[wr][wc]:
                                has_wall_nearby = True
                                break
                    if not has_wall_nearby:
                        continue

                    px = nc * ts + ts // 2
                    py = nr * ts + ts // 2
                    dist_to_player = math.hypot(px - player_x, py - player_y)
                    dist_to_self = math.hypot(px - self.pos_x, py - self.pos_y)

                    # Score : préférer distance idéale au joueur (~120px) et proche de soi
                    score = -abs(dist_to_player - self.COVER_RANGE) - dist_to_self * 0.3
                    if score > best_score:
                        best_score = score
                        best = (px, py)
        return best

    def update(self, player, projectile_group, snd_enemy_laser=None):
        dist_to_player = math.hypot(self.pos_x - player.pos_x, self.pos_y - player.pos_y)
        self.has_line_of_sight = self._check_los(player.pos_x, player.pos_y)

        # Transitions d'état IA
        if dist_to_player > self.DETECTION_RANGE:
            self.state = 'patrol'
        elif self.state == 'patrol' and dist_to_player < self.DETECTION_RANGE:
            self.state = 'chase'
        elif self.state == 'chase' and dist_to_player < self.COVER_RANGE * 1.5:
            # Chercher une couverture
            cover = self._find_cover_near(player.pos_x, player.pos_y)
            if cover:
                self.cover_pos = cover
                self.state = 'cover_seek'
            else:
                self.state = 'cover_fire'  # Pas de couverture, tirer sur place
        elif self.state == 'cover_seek':
            if self.cover_pos:
                d = math.hypot(self.pos_x - self.cover_pos[0], self.pos_y - self.cover_pos[1])
                if d < 12:
                    self.state = 'cover_fire'
                    self.cover_timer = random.randint(120, 300)
            else:
                self.state = 'chase'
        elif self.state == 'cover_fire':
            self.cover_timer -= 1
            if self.cover_timer <= 0 or dist_to_player > self.DETECTION_RANGE * 1.2:
                self.state = 'chase'
                self.cover_pos = None

        # Mouvement selon l'état
        step_x, step_y = 0.0, 0.0

        if self.state == 'patrol':
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_dir_x = random.choice([-1, 0, 1])
                self.patrol_dir_y = random.choice([-1, 0, 1])
                self.patrol_timer = random.randint(60, 180)
            step_x = self.patrol_dir_x * self.SPEED * 0.4
            step_y = self.patrol_dir_y * self.SPEED * 0.4

        elif self.state == 'chase':
            dx = player.pos_x - self.pos_x
            dy = player.pos_y - self.pos_y
            if dist_to_player > 1:
                step_x = (dx / dist_to_player) * self.SPEED
                step_y = (dy / dist_to_player) * self.SPEED

        elif self.state == 'cover_seek' and self.cover_pos:
            dx = self.cover_pos[0] - self.pos_x
            dy = self.cover_pos[1] - self.pos_y
            d = math.hypot(dx, dy)
            if d > 1:
                step_x = (dx / d) * self.SPEED * 1.2
                step_y = (dy / d) * self.SPEED * 1.2

        # cover_fire : immobile, on tire

        # Orientation vers le joueur quand détecté
        if dist_to_player < self.DETECTION_RANGE:
            self.angle = math.degrees(math.atan2(
                -(player.pos_y - self.pos_y), player.pos_x - self.pos_x))
        elif step_x != 0 or step_y != 0:
            self.angle = math.degrees(math.atan2(-step_y, step_x))

        # Déplacement X avec collision
        if step_x != 0:
            self.pos_x += step_x
            self.hitbox.centerx = round(self.pos_x)
            for w in self.tilemap.get_colliding_walls(self.hitbox):
                if self.hitbox.colliderect(w):
                    if step_x > 0:
                        self.hitbox.right = w.left
                    else:
                        self.hitbox.left = w.right
                    self.pos_x = float(self.hitbox.centerx)
                    self.patrol_dir_x = -self.patrol_dir_x

        # Déplacement Y avec collision
        if step_y != 0:
            self.pos_y += step_y
            self.hitbox.centery = round(self.pos_y)
            for w in self.tilemap.get_colliding_walls(self.hitbox):
                if self.hitbox.colliderect(w):
                    if step_y > 0:
                        self.hitbox.bottom = w.top
                    else:
                        self.hitbox.top = w.bottom
                    self.pos_y = float(self.hitbox.centery)
                    self.patrol_dir_y = -self.patrol_dir_y

        self.pos_x = max(20.0, min(self.tilemap.map_width - 20.0, self.pos_x))
        self.pos_y = max(20.0, min(self.tilemap.map_height - 20.0, self.pos_y))
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))

        # Tir double synchronisé (tous les ennemis tirent au même moment)
        can_fire = (self.state in ('chase', 'cover_fire') and
                    self.has_line_of_sight and
                    dist_to_player < self.DETECTION_RANGE)

        if can_fire and (self._global_fire_clock % self.FIRE_INTERVAL == 0):
            fire_angle = math.degrees(math.atan2(
                -(player.pos_y - self.pos_y), player.pos_x - self.pos_x))

            # 2 tirs simultanés (un par épaule) — le son est joué une seule fois
            perp_rad = math.radians(fire_angle + 90)
            offset = 8
            ox = math.cos(perp_rad) * offset
            oy = -math.sin(perp_rad) * offset

            proj_l = Projectile(self.pos_x + ox, self.pos_y + oy, fire_angle, False, self.tilemap)
            proj_r = Projectile(self.pos_x - ox, self.pos_y - oy, fire_angle, False, self.tilemap)
            projectile_group.add(proj_l, proj_r)

            if snd_enemy_laser:
                snd_enemy_laser.play()

        # Rotation de l'image
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def take_hit(self):
        """Reçoit un tir. Retourne True si le robot est détruit."""
        self.hp -= 1
        return self.hp <= 0
