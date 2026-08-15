import pygame
import random
from projectiles import Projectile


#Create the class for the canon
class Canon(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/canon.bmp')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
#Resize the canon image
        self.image = pygame.transform.smoothscale(self.image, (150, 150))
        
        self.all_projectiles = pygame.sprite.Group()
        self.shoot_cooldown = random.randint(0, 100)
        self.shoot_sound = pygame.mixer.Sound('sounds/canon_sound.mp3')
        
    def shoot(self):
        self.shoot_sound.play()
        self.all_projectiles.add(Projectile(self))

        
