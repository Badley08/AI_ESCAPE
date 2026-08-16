import math
import pygame


class Projectile(pygame.sprite.Sprite):
    """Projectile laser (cyan joueur ou rouge ennemi) avec collision murale sub-pixel étanche."""

    SPEED = 9.0

    def __init__(self, x, y, angle_deg, is_player, tilemap):
        super().__init__()
        self.tilemap = tilemap
        self.is_player = is_player

        # L'image de base pointe vers la droite (0°)
        if is_player:
            raw = pygame.image.load('Station_Sector1/level3/assets/player_laser.png').convert_alpha()
            self.base_image = pygame.transform.smoothscale(raw, (28, 10))
        else:
            raw = pygame.image.load('Station_Sector1/level3/assets/enemy_laser.png').convert_alpha()
            self.base_image = pygame.transform.smoothscale(raw, (24, 8))

        self.angle = angle_deg
        rad = math.radians(angle_deg)
        self.vel_x = math.cos(rad) * self.SPEED
        self.vel_y = -math.sin(rad) * self.SPEED

        self.image = pygame.transform.rotate(self.base_image, angle_deg)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect = self.image.get_rect(center=(round(x), round(y)))

        self.lifetime = 160  # Durée de vie maximale

    def update(self):
        # Sous-étapes de déplacement pour empêcher tout passage à travers les murs
        steps = 3
        step_dx = self.vel_x / steps
        step_dy = self.vel_y / steps

        for _ in range(steps):
            self.pos_x += step_dx
            self.pos_y += step_dy
            self.rect.center = (round(self.pos_x), round(self.pos_y))

            # Vérification des limites de l'arène
            if (self.pos_x < 16 or self.pos_x > self.tilemap.map_width - 16 or
                    self.pos_y < 16 or self.pos_y > self.tilemap.map_height - 16):
                self.kill()
                return

            # Vérification de collision murale précise
            if not self.tilemap.is_walkable(self.pos_x, self.pos_y):
                self.kill()
                return

            for w in self.tilemap.get_colliding_walls(self.rect):
                if self.rect.colliderect(w):
                    self.kill()
                    return

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
