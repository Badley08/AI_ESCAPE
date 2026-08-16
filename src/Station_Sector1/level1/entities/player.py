import pygame

class Player(pygame.sprite.Sprite):
    """Robot RTB-O9 pour le Niveau 1 avec orientation dynamique (regarde vers l'avant)."""

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health = 100
        self.max_health = 100
        self.min_health = 0
        self.velocity = 8

        self.images_right = []
        self.images_left = []
        for i in range(1, 7):
            img = pygame.image.load(f'Station_Sector1/level1/assets/{i}.png').convert_alpha()
            aspect_ratio = img.get_width() / img.get_height()
            new_width = int(80 * aspect_ratio)
            scaled = pygame.transform.smoothscale(img, (new_width, 80))
            self.images_right.append(scaled)
            self.images_left.append(pygame.transform.flip(scaled, True, False))

        self.facing_right = True
        self.current_frame = 0.0
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500
        self.is_moving = False

    def damage(self, amount):
        self.health -= amount
        if self.health < self.min_health:
            self.health = self.min_health

    @property
    def is_alive(self):
        return self.health > self.min_health

    def update(self):
        images_list = self.images_right if self.facing_right else self.images_left
        if not self.is_moving:
            self.current_frame = 0.0
            self.image = images_list[0]
        else:
            self.current_frame += 0.15
            if self.current_frame >= len(images_list):
                self.current_frame = 0.0
            self.image = images_list[int(self.current_frame)]

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.is_moving = False

    def animate(self):
        self.is_moving = True

    def move_right(self):
        self.facing_right = True
        self.rect.x += self.velocity
        self.animate()

    def move_left(self):
        self.facing_right = False
        self.rect.x -= self.velocity
        self.animate()

    def move_up(self):
        self.rect.y -= self.velocity
        self.animate()

    def move_down(self):
        self.rect.y += self.velocity
        self.animate()