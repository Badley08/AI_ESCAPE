import math
import pygame


class Player3(pygame.sprite.Sprite):
    """RTB-O9 armé en vue 2D — conserve sa posture verticale naturelle avec retournement gauche/droite et animation fluide."""

    SPEED = 3.8

    def __init__(self, x, y, tilemap):
        super().__init__()
        self.tilemap = tilemap

        # Chargement des 7 frames originales
        sprite_names = [
            'rtb_o9_sprite_01_weapon_lowered.png',
            'rtb_o9_sprite_02_walk_left.png',
            'rtb_o9_sprite_03_walk_right.png',
            'rtb_o9_sprite_04_aim_high.png',
            'rtb_o9_sprite_05_aim_one_hand.png',
            'rtb_o9_sprite_06_walk_passing.png',
            'rtb_o9_sprite_07_walk_right.png',
        ]
        
        # Images de base orientées à droite
        self.images_right = []
        self.images_left = []
        for name in sprite_names:
            img = pygame.image.load(f'Station_Sector1/level3/assets/{name}').convert_alpha()
            ratio = img.get_width() / img.get_height()
            w = int(48 * ratio)
            scaled = pygame.transform.smoothscale(img, (w, 48))
            self.images_right.append(scaled)
            self.images_left.append(pygame.transform.flip(scaled, True, False))

        # Séquence de cycle de marche complet (5 frames)
        self.walk_idx = [0, 1, 5, 2, 6]
        # Frame de visée / tir
        self.aim_idx = 3

        self.facing_right = True
        self.current_frame = 0.0
        self.fire_angle = 0.0  # Angle de lancement balistique du laser

        self.image = self.images_right[0]
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.hitbox = pygame.Rect(0, 0, 16, 16)
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
        """Oriente le visage et le regard de RTB-O9 vers le curseur sans rotation déformante."""
        dx = mouse_world_x - self.pos_x
        dy = mouse_world_y - self.pos_y
        
        # Le regard et le corps changent d'orientation vers la droite ou la gauche du curseur
        if dx >= 0:
            self.facing_right = True
        else:
            self.facing_right = False

        # Angle balistique pour la trajectoire du laser
        self.fire_angle = math.degrees(math.atan2(-dy, dx))

    def try_shoot(self):
        """Déclenche un tir plasma si le cooldown est prêt."""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 14
            self.is_shooting = True
            return True
        return False

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        img_set = self.images_right if self.facing_right else self.images_left

        # Choix de la posture/animation naturelle
        if self.is_shooting or self.shoot_cooldown > 8:
            # Posture de visée avec arme levée
            self.image = img_set[self.aim_idx]
            self.is_shooting = False
        elif self.is_moving:
            # Cycle de marche fluide
            self.current_frame += 0.16
            if self.current_frame >= len(self.walk_idx):
                self.current_frame = 0.0
            frame_no = self.walk_idx[int(self.current_frame)]
            self.image = img_set[frame_no]
        else:
            # Posture d'attente au repos
            self.current_frame = 0.0
            self.image = img_set[0]

        # Le sprite reste toujours droit et ancré à sa hitbox
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Décharge passive douce
        self.battery -= 0.003
        if self.battery < 0:
            self.battery = 0.0

    def take_damage(self, amount):
        self.battery -= amount
        if self.battery < 0:
            self.battery = 0.0

    def restore_battery(self, amount):
        self.battery = min(self.max_battery, self.battery + amount)
