import math
import pygame


class Player3(pygame.sprite.Sprite):
    """RTB-O9 armé — animation de marche fluide, rotation précise vers la visée, tir Clic Gauche ou ESPACE."""

    SPEED = 3.8

    def __init__(self, x, y, tilemap):
        super().__init__()
        self.tilemap = tilemap

        # Chargement et mise à l'échelle des 7 frames
        sprite_names = [
            'rtb_o9_sprite_01_weapon_lowered.png',
            'rtb_o9_sprite_02_walk_left.png',
            'rtb_o9_sprite_03_walk_right.png',
            'rtb_o9_sprite_04_aim_high.png',
            'rtb_o9_sprite_05_aim_one_hand.png',
            'rtb_o9_sprite_06_walk_passing.png',
            'rtb_o9_sprite_07_walk_right.png',
        ]
        self.base_images = []
        for name in sprite_names:
            img = pygame.image.load(f'level3/assets/{name}').convert_alpha()
            ratio = img.get_width() / img.get_height()
            w = int(40 * ratio)
            img = pygame.transform.smoothscale(img, (w, 40))
            self.base_images.append(img)

        # Séquence de marche continue
        self.walk_frames = [
            self.base_images[0],
            self.base_images[1],
            self.base_images[5],
            self.base_images[2],
            self.base_images[6]
        ]
        self.aim_frame = self.base_images[3]

        self.current_frame = 0.0
        # Angle de rotation (0° = vers le bas, 90° = droite, 180° = haut, -90° = gauche)
        self.rot_angle = 0.0
        self.fire_angle = 0.0  # Angle de lancement du projectile (0° = droite, 90° = haut)
        self.image = self.base_images[0]

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.hitbox = pygame.Rect(0, 0, 14, 14)
        self.hitbox.center = (round(self.pos_x), round(self.pos_y))
        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.is_moving = False
        self.is_shooting = False
        self.shoot_cooldown = 0
        self.battery = 100.0
        self.max_battery = 100.0

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

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        dx *= self.SPEED
        dy *= self.SPEED

        if dx != 0 or dy != 0:
            self.is_moving = True

            # Déplacement X avec résolution de collision
            self.pos_x += dx
            self.hitbox.centerx = round(self.pos_x)
            for w in self.tilemap.get_colliding_walls(self.hitbox):
                if self.hitbox.colliderect(w):
                    if dx > 0:
                        self.hitbox.right = w.left
                    elif dx < 0:
                        self.hitbox.left = w.right
                    self.pos_x = float(self.hitbox.centerx)

            # Déplacement Y avec résolution de collision
            self.pos_y += dy
            self.hitbox.centery = round(self.pos_y)
            for w in self.tilemap.get_colliding_walls(self.hitbox):
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

    def update_aim(self, mouse_world_x, mouse_world_y):
        """Oriente le corps, le casque et l'arme de RTB-O9 vers le curseur."""
        dx = mouse_world_x - self.pos_x
        dy = mouse_world_y - self.pos_y
        # Angle balistique pour les lasers (0° = droite, 90° = haut)
        self.fire_angle = math.degrees(math.atan2(-dy, dx))
        # Angle de rotation du sprite (car le sprite de base regarde vers le bas = vecteur (0, 1))
        self.rot_angle = -math.degrees(math.atan2(dy, dx)) + 90.0

    def try_shoot(self):
        """Déclenche un tir plasma si le cooldown est écoulé."""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 14  # ~4.3 tirs par seconde à 60 FPS
            self.is_shooting = True
            return True
        return False

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Choix de la frame d'animation
        if self.is_shooting:
            base_frame = self.aim_frame
            self.is_shooting = False
        elif self.is_moving:
            self.current_frame += 0.18
            if self.current_frame >= len(self.walk_frames):
                self.current_frame = 0.0
            base_frame = self.walk_frames[int(self.current_frame)]
        else:
            self.current_frame = 0.0
            base_frame = self.walk_frames[0]

        # Rotation précise vers la cible visée
        self.image = pygame.transform.rotate(base_frame, self.rot_angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Décharge passive
        self.battery -= 0.003
        if self.battery < 0:
            self.battery = 0.0

    def take_damage(self, amount):
        self.battery -= amount
        if self.battery < 0:
            self.battery = 0.0

    def restore_battery(self, amount):
        self.battery = min(self.max_battery, self.battery + amount)
