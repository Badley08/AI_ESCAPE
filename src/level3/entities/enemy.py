import math
import random
import pygame
from level3.entities.projectile import Projectile


class EnemyRobot(pygame.sprite.Sprite):
    """Robot ennemi corrompu de la même génération que RTB-O9."""

    SPEED = 1.8
    DETECTION_RANGE = 280
    FIRE_COOLDOWN = 120  # ~2 secondes à 60 FPS

    def __init__(self, x, y, variant, tilemap):
        super().__init__()
        self.tilemap = tilemap
        self.variant = variant

        # Chargement du sprite selon la variante (1, 2 ou 3)
        sprite_files = {
            1: 'enemy_robot.png',
            2: 'enemy_robot2.png',
            3: 'enemy_robot3.png',
        }
        raw = pygame.image.load(f'level3/assets/{sprite_files.get(variant, "enemy_robot.png")}').convert_alpha()
        ratio = raw.get_width() / raw.get_height()
        size_h = 44 + variant * 4  # Variante 1: 48px, 2: 52px, 3: 56px
        self.base_image = pygame.transform.smoothscale(raw, (int(size_h * ratio), size_h))
        self.image = self.base_image

        self.pos_x = float(x)
        self.pos_y = float(y)
        self.hitbox = pygame.Rect(0, 0, 16, 16)
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Stats selon la variante
        self.max_hp = variant + 1  # 2, 3, 4 HP
        self.hp = self.max_hp
        self.fire_timer = random.randint(30, self.FIRE_COOLDOWN)

        # Patrouille : direction aléatoire
        self.patrol_dir_x = random.choice([-1, 0, 1])
        self.patrol_dir_y = random.choice([-1, 0, 1])
        self.patrol_timer = random.randint(60, 180)
        self.angle = 0.0
        self.chasing = False

    def update(self, player, projectile_group):
        dist = math.hypot(self.pos_x - player.pos_x, self.pos_y - player.pos_y)

        if dist < self.DETECTION_RANGE:
            # Poursuite
            self.chasing = True
            dx = player.pos_x - self.pos_x
            dy = player.pos_y - self.pos_y
            if dist > 0:
                dx /= dist
                dy /= dist
            self.angle = math.degrees(math.atan2(-dy, dx))

            step_x = dx * self.SPEED
            step_y = dy * self.SPEED
        else:
            # Patrouille
            self.chasing = False
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_dir_x = random.choice([-1, 0, 1])
                self.patrol_dir_y = random.choice([-1, 0, 1])
                self.patrol_timer = random.randint(60, 180)

            step_x = self.patrol_dir_x * self.SPEED * 0.5
            step_y = self.patrol_dir_y * self.SPEED * 0.5
            if self.patrol_dir_x != 0 or self.patrol_dir_y != 0:
                self.angle = math.degrees(math.atan2(-self.patrol_dir_y, self.patrol_dir_x))

        # Déplacement X avec collision
        self.pos_x += step_x
        self.hitbox.centerx = round(self.pos_x)
        for w in self.tilemap.get_colliding_walls(self.hitbox):
            if self.hitbox.colliderect(w):
                if step_x > 0:
                    self.hitbox.right = w.left
                elif step_x < 0:
                    self.hitbox.left = w.right
                self.pos_x = float(self.hitbox.centerx)
                self.patrol_dir_x = -self.patrol_dir_x

        # Déplacement Y avec collision
        self.pos_y += step_y
        self.hitbox.centery = round(self.pos_y)
        for w in self.tilemap.get_colliding_walls(self.hitbox):
            if self.hitbox.colliderect(w):
                if step_y > 0:
                    self.hitbox.bottom = w.top
                elif step_y < 0:
                    self.hitbox.top = w.bottom
                self.pos_y = float(self.hitbox.centery)
                self.patrol_dir_y = -self.patrol_dir_y

        # Limites de la carte
        self.pos_x = max(20.0, min(self.tilemap.map_width - 20.0, self.pos_x))
        self.pos_y = max(20.0, min(self.tilemap.map_height - 20.0, self.pos_y))
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))

        # Tir double (un laser par épaule)
        self.fire_timer -= 1
        if self.chasing and self.fire_timer <= 0 and dist < self.DETECTION_RANGE:
            self.fire_timer = self.FIRE_COOLDOWN + random.randint(-20, 20)
            fire_angle = math.degrees(math.atan2(-(player.pos_y - self.pos_y),
                                                   player.pos_x - self.pos_x))
            # Décalage perpendiculaire pour simuler les 2 canons d'épaule
            perp_rad = math.radians(fire_angle + 90)
            offset = 8  # pixels d'écart entre les 2 canons
            ox = math.cos(perp_rad) * offset
            oy = -math.sin(perp_rad) * offset

            proj_l = Projectile(self.pos_x + ox, self.pos_y + oy, fire_angle, False, self.tilemap)
            proj_r = Projectile(self.pos_x - ox, self.pos_y - oy, fire_angle, False, self.tilemap)
            projectile_group.add(proj_l)
            projectile_group.add(proj_r)

        # Rotation de l'image
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def take_hit(self):
        """Reçoit un tir. Retourne True si le robot est détruit."""
        self.hp -= 1
        return self.hp <= 0
