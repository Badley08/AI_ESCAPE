import pygame

#Create the class for the projectiles
class Projectile(pygame.sprite.Sprite):
    def __init__(self, canon):
        super().__init__()
        #Define the projectile speed
        self.velocity = 5
        #Define the damage of the projectile
        self.damage = 5
        #Link the projectile to its canon
        self.canon = canon
        #Load and resize the projectile image
        self.image = pygame.image.load('assets/tir.bmp')
        self.image = pygame.transform.smoothscale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        #Position the projectile at the canon
        self.rect.x = canon.rect.x
        self.rect.y = canon.rect.y + 30
        
    def remove(self):
        #Remove the projectile from its canon group
        if self in self.canon.all_projectiles:
            self.canon.all_projectiles.remove(self)
        
    def move(self):
        #Move the projectile to the left
        self.rect.x -= self.velocity
        
        #Remove if off screen
        if self.rect.x < 0:
            self.remove()
