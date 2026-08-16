import pygame

#Create the class for the explosion effect (used on game over screen)
class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        #Load and resize the explosion image
        self.image = pygame.image.load('level1/assets/explosion.png')
        self.image = pygame.transform.smoothscale(self.image, (300, 300))
        self.rect = self.image.get_rect()
        #Position the explosion at the center
        self.rect.centerx = x
        self.rect.centery = y
