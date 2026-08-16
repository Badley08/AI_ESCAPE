import pygame
import random
from level1.entities.projectiles import Projectile


#Create the class for the canon
class Canon(pygame.sprite.Sprite):

    def __init__(self, x, y, initial_cooldown=0):
        super().__init__()
        self.image = pygame.image.load('level1/assets/canon.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
#Resize the canon image
        self.image = pygame.transform.smoothscale(self.image, (150, 150))
        
        self.all_projectiles = pygame.sprite.Group()
        self.shoot_cooldown = initial_cooldown
        self.shoot_sound = pygame.mixer.Sound('level1/sounds/canon_sound.mp3')
        
    def shoot(self):
        self.shoot_sound.play()
        self.all_projectiles.add(Projectile(self))

        
