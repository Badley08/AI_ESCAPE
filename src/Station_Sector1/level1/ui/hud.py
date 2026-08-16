import pygame

#Create the class for the HUD (heads-up display)
class HUD:

    def __init__(self):
        #Define fonts for the HUD
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        #Primary color of the game (blue)
        self.color_blue = (0, 150, 255)
        self.color_dark_blue = (0, 80, 160)
        self.color_white = (255, 255, 255)
        self.color_red = (255, 50, 50)
        self.color_bg = (20, 20, 40)
        #Load the damage overlay image
        self.damage_image = pygame.image.load('Station_Sector1/level1/assets/damage.png')
        self.damage_image = pygame.transform.smoothscale(self.damage_image, (1080, 720))
        self.damage_image.set_alpha(160)
        #Timer to show the damage overlay
        self.damage_flash_timer = 0
        #Timer to show the intro text
        self.intro_timer = 180

    def trigger_damage_flash(self):
        #Trigger the damage overlay for a few frames
        self.damage_flash_timer = 12

    def draw_health_bar(self, surface, player):
        #Define the health bar dimensions
        bar_x = 20
        bar_y = 20
        bar_width = 250
        bar_height = 25
        #Calculate the fill based on the player health
        fill_ratio = player.health / player.max_health
        fill_width = int(bar_width * fill_ratio)
        #Draw the background of the health bar
        pygame.draw.rect(surface, self.color_bg, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=5)
        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        #Choose color based on health level
        if fill_ratio > 0.5:
            bar_color = self.color_blue
        elif fill_ratio > 0.25:
            bar_color = (255, 165, 0)
        else:
            bar_color = self.color_red
        #Draw the fill of the health bar
        if fill_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)
        #Draw the border of the health bar
        pygame.draw.rect(surface, self.color_blue, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2, border_radius=5)
        #Draw the health text
        health_text = self.font_small.render(f"HP: {player.health}/{player.max_health}", True, self.color_white)
        surface.blit(health_text, (bar_x + bar_width + 10, bar_y))

    def draw_timer(self, surface, seconds_left):
        #Draw the countdown timer at the top center
        timer_text = self.font_large.render(f"{seconds_left}", True, self.color_blue)
        timer_rect = timer_text.get_rect(centerx=540, y=15)
        surface.blit(timer_text, timer_rect)
        #Draw the label under the timer
        label_text = self.font_small.render("SECONDS LEFT", True, self.color_white)
        label_rect = label_text.get_rect(centerx=540, y=70)
        surface.blit(label_text, label_rect)

    def draw_intro(self, surface):
        #Draw the intro text only during the first few seconds
        if self.intro_timer > 0:
            self.intro_timer -= 1
            #Calculate alpha for fade out effect
            alpha = min(255, self.intro_timer * 4)
            #Draw the level title
            title_text = self.font_large.render("TEST ALPHA", True, self.color_blue)
            title_rect = title_text.get_rect(centerx=540, centery=300)
            #Draw the objective text
            obj_text = self.font_medium.render("Survive 60 seconds", True, self.color_white)
            obj_rect = obj_text.get_rect(centerx=540, centery=360)
            #Create a transparent surface for fade effect
            intro_surface = pygame.Surface((1080, 720), pygame.SRCALPHA)
            #Render texts with alpha onto the surface
            title_with_alpha = self.font_large.render("TEST ALPHA", True, (*self.color_blue, alpha))
            obj_with_alpha = self.font_medium.render("Survive 60 seconds", True, (*self.color_white, alpha))
            intro_surface.blit(title_with_alpha, title_rect)
            intro_surface.blit(obj_with_alpha, obj_rect)
            surface.blit(intro_surface, (0, 0))

    def draw_damage_flash(self, surface):
        #Draw the damage overlay if the timer is active
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            surface.blit(self.damage_image, (0, 0))

    def draw(self, surface, player, seconds_left):
        #Draw all HUD elements
        self.draw_health_bar(surface, player)
        self.draw_timer(surface, seconds_left)
        self.draw_intro(surface)
        self.draw_damage_flash(surface)
