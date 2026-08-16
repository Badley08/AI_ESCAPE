import pygame

#Create the first class for the player
class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        super().__init__()
        #Define that the player is linked to the game
        self.game = game
        self.health = 100
        self.max_health = 100
        self.min_health = 0
        self.velocity = 8
        self.images = []
        for i in range(1, 7):
            img = pygame.image.load(f'level1/assets/{i}.png')
            # Scale proportionally to height 80 to avoid distortion
            aspect_ratio = img.get_width() / img.get_height()
            new_width = int(80 * aspect_ratio)
            img = pygame.transform.smoothscale(img, (new_width, 80))
            self.images.append(img)
            
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500
        self.is_moving = False

    def damage(self, amount):
        #Apply damage to the player
        self.health -= amount
        #Clamp health to minimum
        if self.health < self.min_health:
            self.health = self.min_health

    @property
    def is_alive(self):
        #Check if the player is still alive
        return self.health > self.min_health

    def update(self):
        if not self.is_moving:
            self.current_frame = 0
            self.image = self.images[0]
        else:
            self.current_frame += 0.15
            if self.current_frame >= len(self.images):
                self.current_frame = 0
            self.image = self.images[int(self.current_frame)]
            
        # Keep the rect centered based on previous position to avoid jittering
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Reset moving flag for next frame
        self.is_moving = False

    def animate(self):
        self.is_moving = True

    def move_right(self):
        self.rect.x += self.velocity
        self.animate()

    def move_left(self):
        self.rect.x -= self.velocity
        self.animate()

    def move_up(self):
        self.rect.y -= self.velocity
        self.animate()

    def move_down(self):
        self.rect.y += self.velocity
        self.animate()