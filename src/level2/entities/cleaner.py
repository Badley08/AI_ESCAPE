import math
import pygame

class CleanerRobot(pygame.sprite.Sprite):
    """Véhicule de nettoyage au sol avec collisions strictes intégrales."""

    SPEED = 2.2

    def __init__(self, x, y, tilemap):
        super().__init__()
        self.tilemap = tilemap

        # Image du véhicule (+8px)
        raw_img = pygame.image.load('level2/cleaner_robot.png').convert_alpha()
        self.base_image = pygame.transform.smoothscale(raw_img, (52, 48))
        self.image = self.base_image

        self.pos_x = float(x)
        self.pos_y = float(y)

        # Hitbox de navigation
        self.hitbox = pygame.Rect(0, 0, 10, 10)
        self.hitbox.center = (int(x), int(y))
        
        # Hitbox d'attaque (pinces du véhicule)
        self.attack_hitbox = pygame.Rect(0, 0, 28, 28)
        self.attack_hitbox.center = self.hitbox.center

        self.rect = self.image.get_rect(center=self.hitbox.center)

        self.path = []
        self.recalc_timer = 0
        self.step_timer = 0

        try:
            self.footstep_sound = pygame.mixer.Sound('level2/sounds/cleaner_footsteps.mp3')
        except Exception:
            self.footstep_sound = None

    def update_path(self, player_pos):
        self.path = self.tilemap.get_path(
            (self.hitbox.centerx, self.hitbox.centery),
            player_pos
        )

    def update(self, player):
        self.recalc_timer += 1
        if self.recalc_timer >= 16 or not self.path:
            self.recalc_timer = 0
            self.update_path((player.pos_x, player.pos_y))

        # Déplacement dans les couloirs
        if self.path:
            target_x, target_y = self.path[0]
            dx = target_x - self.hitbox.centerx
            dy = target_y - self.hitbox.centery
            dist = math.hypot(dx, dy)

            if dist < 6:
                self.path.pop(0)
            elif dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                step_x = dir_x * self.SPEED
                step_y = dir_y * self.SPEED

                # Résolution X par étapes entières
                int_dx = int(step_x) if abs(step_x) >= 1 else (1 if step_x > 0 else (-1 if step_x < 0 else 0))
                self.hitbox.x += int_dx
                for w in self.tilemap.get_colliding_walls(self.hitbox):
                    if self.hitbox.colliderect(w):
                        if int_dx > 0:
                            self.hitbox.right = w.left
                        elif int_dx < 0:
                            self.hitbox.left = w.right

                # Résolution Y par étapes entières
                int_dy = int(step_y) if abs(step_y) >= 1 else (1 if step_y > 0 else (-1 if step_y < 0 else 0))
                self.hitbox.y += int_dy
                for w in self.tilemap.get_colliding_walls(self.hitbox):
                    if self.hitbox.colliderect(w):
                        if int_dy > 0:
                            self.hitbox.bottom = w.top
                        elif int_dy < 0:
                            self.hitbox.top = w.bottom

                self.pos_x = float(self.hitbox.centerx)
                self.pos_y = float(self.hitbox.centery)
                self.attack_hitbox.center = self.hitbox.center

                # Orientation véhicule
                target_angle = math.degrees(math.atan2(-dy, dx))
                self.image = pygame.transform.rotate(self.base_image, target_angle - 90)

        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Audio spatial
        dist_to_player = math.hypot(self.pos_x - player.pos_x, self.pos_y - player.pos_y)
        self.step_timer += 1
        if self.step_timer >= 26:
            self.step_timer = 0
            if dist_to_player < 450 and self.footstep_sound:
                vol = max(0.05, min(0.85, 1.0 - (dist_to_player / 450.0)))
                self.footstep_sound.set_volume(vol)
                self.footstep_sound.play()

    def stop_sound(self):
        if self.footstep_sound:
            self.footstep_sound.stop()
