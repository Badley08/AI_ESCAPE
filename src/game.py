import pygame
from player import Player
from canon import Canon
from explosion import Explosion

#Create a second class that represents the game
class Game:

    def __init__(self):
        #Generate our player
        self.player = Player(self)
        #Generate our canons
        self.canons = pygame.sprite.Group()
        # Add 3 canons, same X, Y offseted
        self.canons.add(Canon(900, 560))
        self.canons.add(Canon(900, 399))
        self.canons.add(Canon(900, 480))
        self.pressed = {}
        #Define the game state (playing, game_over, victory)
        self.state = "playing"
        #Define the timer for 60 seconds
        self.total_time = 60
        self.start_ticks = pygame.time.get_ticks()
        #Group for explosion effects on game over
        self.explosions = pygame.sprite.Group()
        
        # Load damage sound
        self.damage_sound = pygame.mixer.Sound('sounds/boom.mp3')
        self.damage_sound.set_volume(0.2)

    def get_seconds_left(self):
        #Calculate how many seconds are left
        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        seconds_left = self.total_time - int(elapsed)
        #Clamp to 0 minimum
        if seconds_left < 0:
            seconds_left = 0
        return seconds_left

    def check_collision(self, sprite, group):
        #Check if the sprite collides with any sprite in the group
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)

    def update(self, hud):
        #Only update if the game is still playing
        if self.state != "playing":
            return

        #Update player logic (like animation idle state)
        self.player.update()

        #Check the timer
        seconds_left = self.get_seconds_left()

        #If the timer runs out and the player is alive, victory
        if seconds_left <= 0 and self.player.is_alive:
            self.state = "victory"
            return

        #Update canons shooting and projectiles
        for canon in self.canons:
            canon.shoot_cooldown -= 1
            if canon.shoot_cooldown <= 0:
                canon.shoot()
                canon.shoot_cooldown = 100

            #Update each projectile
            for projectile in list(canon.all_projectiles):
                projectile.move()

                #Check collision between this projectile and the player
                hitbox = self.player.rect.inflate(-30, -30)
                if hitbox.colliderect(projectile.rect):
                    #Apply damage to the player
                    self.player.damage(projectile.damage)
                    #Play the damage sound
                    self.damage_sound.play()
                    #Trigger the damage flash on the HUD
                    hud.trigger_damage_flash()
                    #Remove the projectile
                    projectile.remove()

                    #If the player is dead, game over
                    if not self.player.is_alive:
                        self.state = "game_over"
                        #Spawn the explosion at the player position
                        self.explosions.add(Explosion(self.player.rect.centerx, self.player.rect.centery))
                        return