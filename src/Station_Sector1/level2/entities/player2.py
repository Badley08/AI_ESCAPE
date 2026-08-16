import math
import pygame

class Player2(pygame.sprite.Sprite):
    """Robot RTB-O9 avec rotation dynamique du regard dans la direction de déplacement."""

    SPEED = 3.6

    def __init__(self, x, y, tilemap):
        super().__init__()
        self.tilemap = tilemap

        # Chargement des 5 frames de marche (+4px de taille)
        self.base_images = []
        for i in range(1, 6):
            img = pygame.image.load(f'Station_Sector1/level2/{i}.png').convert_alpha()
            ratio = img.get_width() / img.get_height()
            w = int(36 * ratio)
            img = pygame.transform.smoothscale(img, (w, 36))
            self.base_images.append(img)

        self.current_frame = 0.0
        self.current_angle = 0.0  # Angle de regard (0° = vers le bas / avant par défaut)
        self.image = self.base_images[0]

        # Boîte de données portée
        raw_box = pygame.image.load('Station_Sector1/level2/data_fragment.png').convert_alpha()
        self.carried_box_img = pygame.transform.smoothscale(raw_box, (20, 20))

        # Position flottante
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Hitbox calibrée pour glisser dans les couloirs
        self.hitbox = pygame.Rect(0, 0, 12, 12)
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.is_moving = False
        self.battery = 100.0
        self.max_battery = 100.0
        self.carried_cores = 0

    def move(self, keys):
        dx = 0
        dy = 0
        if keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            dx += 1
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            dx -= 1
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            dy += 1
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            dy -= 1

        if dx != 0 or dy != 0:
            # Calcul de l'angle précis pour que le visage et les yeux regardent dans la direction du mouvement
            # L'image de base (1.png) regarde vers le bas (vecteur (0, 1)), donc angle = -atan2(dy, dx) + 90°
            self.current_angle = -math.degrees(math.atan2(dy, dx)) + 90.0

            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            speed = self.SPEED * (0.94 if self.carried_cores > 0 else 1.0)
            dx *= speed
            dy *= speed

            self.is_moving = True
            
            # Déplacement X avec résolution de collision
            self.pos_x += dx
            self.hitbox.centerx = round(self.pos_x)
            walls = self.tilemap.get_colliding_walls(self.hitbox)
            for w in walls:
                if self.hitbox.colliderect(w):
                    if dx > 0:
                        self.hitbox.right = w.left
                    elif dx < 0:
                        self.hitbox.left = w.right
                    self.pos_x = float(self.hitbox.centerx)

            # Déplacement Y avec résolution de collision
            self.pos_y += dy
            self.hitbox.centery = round(self.pos_y)
            walls = self.tilemap.get_colliding_walls(self.hitbox)
            for w in walls:
                if self.hitbox.colliderect(w):
                    if dy > 0:
                        self.hitbox.bottom = w.top
                    elif dy < 0:
                        self.hitbox.top = w.bottom
                    self.pos_y = float(self.hitbox.centery)

            self.pos_x = max(16.0, min(self.tilemap.map_width - 16.0, self.pos_x))
            self.pos_y = max(16.0, min(self.tilemap.map_height - 16.0, self.pos_y))
            self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        else:
            self.is_moving = False

    def update(self):
        # Animation de marche
        if self.is_moving:
            self.current_frame += 0.18
            if self.current_frame >= len(self.base_images):
                self.current_frame = 0.0
            base_frame = self.base_images[int(self.current_frame)]
        else:
            self.current_frame = 0.0
            base_frame = self.base_images[0]

        # Rotation pour que le visage soit toujours orienté vers l'avant du mouvement
        self.image = pygame.transform.rotate(base_frame, self.current_angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Décharge passive très douce (environ 9 minutes d'autonomie pure)
        self.battery -= 0.003
        if self.battery < 0:
            self.battery = 0.0

    def draw_carried_indicator(self, surface, offset_x, offset_y):
        if self.carried_cores > 0:
            bx = int(self.pos_x + offset_x - 10)
            by = int(self.pos_y + offset_y - 28)
            surface.blit(self.carried_box_img, (bx, by))

    def restore_battery(self, amount=15.0):
        self.battery = min(self.max_battery, self.battery + amount)
