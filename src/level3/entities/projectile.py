import math
import pygame


class Projectile(pygame.sprite.Sprite):
    """Projectile laser (cyan joueur ou rouge ennemi) avec collision murale."""

    SPEED = 8.0

    def __init__(self, x, y, angle_deg, is_player, tilemap):
        super().__init__()
        self.tilemap = tilemap
        self.is_player = is_player

        # L'image de base pointe vers la droite (angle 0°)
        if is_player:
            raw = pygame.image.load('level3/assets/player_laser.png').convert_alpha()
            self.base_image = pygame.transform.smoothscale(raw, (28, 10))
        else:
            raw = pygame.image.load('level3/assets/enemy_laser.png').convert_alpha()
            self.base_image = pygame.transform.smoothscale(raw, (24, 8))

        self.angle = angle_deg
        rad = math.radians(angle_deg)
        self.vel_x = math.cos(rad) * self.SPEED
        self.vel_y = -math.sin(rad) * self.SPEED

        self.image = pygame.transform.rotate(self.base_image, angle_deg)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect = self.image.get_rect(center=(round(x), round(y)))

        self.lifetime = 180  # 3 secondes max

    def update(self):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.rect.center = (round(self.pos_x), round(self.pos_y))
        self.lifetime -= 1

        # Destruction si hors carte, mur, ou fin de vie
        if self.lifetime <= 0:
            self.kill()
            return

        if (self.pos_x < 0 or self.pos_x > self.tilemap.map_width or
                self.pos_y < 0 or self.pos_y > self.tilemap.map_height):
            self.kill()
            return

        if not self.tilemap.is_walkable(self.pos_x, self.pos_y):
            self.kill()
