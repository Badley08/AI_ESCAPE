import math
import random
import pygame
from level3.entities.projectile import Projectile


class EnemyRobot(pygame.sprite.Sprite):
    """Robot ennemi en vue 2D — posture droite naturelle avec orientation gauche/droite et IA de garde/patrouille."""

    SPEED = 2.0
    DETECTION_RANGE = 280
    COVER_RANGE = 120
    FIRE_INTERVAL = 90

    _global_fire_clock = 0

    @classmethod
    def tick_global_clock(cls):
        cls._global_fire_clock += 1

    @classmethod
    def reset_global_clock(cls):
        cls._global_fire_clock = 0

    def __init__(self, x, y, variant, tilemap, guard_terminal=None):
        super().__init__()
        self.tilemap = tilemap
        self.variant = variant
        self.is_guard = (variant == 1)  # Robot noir = Garde de terminal
        self.guard_terminal = guard_terminal

        sprite_files = {1: 'enemy_robot.png', 2: 'enemy_robot2.png', 3: 'enemy_robot3.png'}
        raw = pygame.image.load(f'level3/assets/{sprite_files.get(variant, "enemy_robot.png")}').convert_alpha()
        ratio = raw.get_width() / raw.get_height()
        size_h = 48 + variant * 4

        # Images droite et gauche pré-générées pour posture 2D naturelle
        scaled = pygame.transform.smoothscale(raw, (int(size_h * ratio), size_h))
        self.image_right = scaled
        self.image_left = pygame.transform.flip(scaled, True, False)
        self.facing_right = True
        self.image = self.image_right

        self.pos_x = float(x)
        self.pos_y = float(y)
        self.hitbox = pygame.Rect(0, 0, 16, 16)
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.max_hp = variant + 1
        self.hp = self.max_hp

        # États IA
        self.state = 'guard' if self.is_guard else 'patrol'
        self.patrol_dir_x = random.choice([-1, 0, 1])
        self.patrol_dir_y = random.choice([-1, 0, 1])
        self.patrol_timer = random.randint(60, 180)
        self.cover_pos = None
        self.cover_timer = 0
        self.investigating_target = None
        self.has_line_of_sight = False

    def alert_to_terminal(self, terminal_pos):
        if self.is_guard:
            self.investigating_target = terminal_pos
            self.state = 'investigate'

    def _check_los(self, target_x, target_y):
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
        best = None
        best_score = -999
        ts = self.tilemap.tile_size
        search_r = 8
        cx = int(self.pos_x) // ts
        cy = int(self.pos_y) // ts

        for dr in range(-search_r, search_r + 1, 2):
            for dc in range(-search_r, search_r + 1, 2):
                nc, nr = cx + dc, cy + dr
                if 0 <= nc < self.tilemap.cols and 0 <= nr < self.tilemap.rows:
                    if not self.tilemap.grid[nr][nc]:
                        continue
                    has_wall = False
                    for wd in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        wc, wr = nc + wd[0], nr + wd[1]
                        if 0 <= wc < self.tilemap.cols and 0 <= wr < self.tilemap.rows:
                            if not self.tilemap.grid[wr][wc]:
                                has_wall = True
                                break
                    if not has_wall:
                        continue

                    px = nc * ts + ts // 2
                    py = nr * ts + ts // 2
                    dist_to_p = math.hypot(px - player_x, py - player_y)
                    dist_to_self = math.hypot(px - self.pos_x, py - self.pos_y)
                    score = -abs(dist_to_p - self.COVER_RANGE) - dist_to_self * 0.3
                    if score > best_score:
                        best_score = score
                        best = (px, py)
        return best

    def update(self, player, projectile_group, snd_enemy_laser=None):
        dist_to_player = math.hypot(self.pos_x - player.pos_x, self.pos_y - player.pos_y)
        self.has_line_of_sight = self._check_los(player.pos_x, player.pos_y)

        # Transitions IA
        if dist_to_player < self.DETECTION_RANGE and self.has_line_of_sight:
            if self.state not in ('chase', 'cover_seek', 'cover_fire'):
                self.state = 'chase'
        elif dist_to_player > self.DETECTION_RANGE * 1.3:
            if self.state in ('chase', 'cover_seek', 'cover_fire'):
                if self.is_guard and self.investigating_target:
                    self.state = 'investigate'
                elif self.is_guard:
                    self.state = 'guard'
                else:
                    self.state = 'patrol'

        if self.state == 'chase' and dist_to_player < self.COVER_RANGE * 1.4:
            cover = self._find_cover_near(player.pos_x, player.pos_y)
            if cover:
                self.cover_pos = cover
                self.state = 'cover_seek'
            else:
                self.state = 'cover_fire'
        elif self.state == 'cover_seek':
            if self.cover_pos:
                d = math.hypot(self.pos_x - self.cover_pos[0], self.pos_y - self.cover_pos[1])
                if d < 12:
                    self.state = 'cover_fire'
                    self.cover_timer = random.randint(100, 240)
            else:
                self.state = 'chase'
        elif self.state == 'cover_fire':
            self.cover_timer -= 1
            if self.cover_timer <= 0:
                self.state = 'chase'
                self.cover_pos = None

        # Déplacement
        step_x, step_y = 0.0, 0.0

        if self.state == 'guard':
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_dir_x = random.choice([-1, 0, 1])
                self.patrol_dir_y = random.choice([-1, 0, 1])
                self.patrol_timer = random.randint(80, 200)
            step_x = self.patrol_dir_x * self.SPEED * 0.25
            step_y = self.patrol_dir_y * self.SPEED * 0.25

        elif self.state == 'investigate' and self.investigating_target:
            tx, ty = self.investigating_target
            dx = tx - self.pos_x
            dy = ty - self.pos_y
            d = math.hypot(dx, dy)
            if d > 20:
                step_x = (dx / d) * self.SPEED * 0.8
                step_y = (dy / d) * self.SPEED * 0.8
            else:
                self.state = 'guard'
                self.investigating_target = None

        elif self.state == 'patrol':
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_dir_x = random.choice([-1, 0, 1])
                self.patrol_dir_y = random.choice([-1, 0, 1])
                self.patrol_timer = random.randint(60, 180)
            step_x = self.patrol_dir_x * self.SPEED * 0.5
            step_y = self.patrol_dir_y * self.SPEED * 0.5

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
                step_x = (dx / d) * self.SPEED * 1.1
                step_y = (dy / d) * self.SPEED * 1.1

        # Orientation naturelle gauche/droite
        if dist_to_player < self.DETECTION_RANGE:
            self.facing_right = (player.pos_x >= self.pos_x)
        elif step_x != 0:
            self.facing_right = (step_x > 0)

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

        # Tir double synchronisé
        can_fire = (self.state in ('chase', 'cover_fire') and
                    self.has_line_of_sight and
                    dist_to_player < self.DETECTION_RANGE)

        if can_fire and (self._global_fire_clock % self.FIRE_INTERVAL == 0):
            fire_angle = math.degrees(math.atan2(-(player.pos_y - self.pos_y), player.pos_x - self.pos_x))
            perp_rad = math.radians(fire_angle + 90)
            offset = 8
            ox = math.cos(perp_rad) * offset
            oy = -math.sin(perp_rad) * offset

            proj_l = Projectile(self.pos_x + ox, self.pos_y + oy, fire_angle, False, self.tilemap)
            proj_r = Projectile(self.pos_x - ox, self.pos_y - oy, fire_angle, False, self.tilemap)
            projectile_group.add(proj_l, proj_r)

            if snd_enemy_laser:
                snd_enemy_laser.play()

        # Image orientée gauche/droite sans rotation inclinée
        self.image = self.image_right if self.facing_right else self.image_left
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def take_hit(self):
        self.hp -= 1
        return self.hp <= 0
