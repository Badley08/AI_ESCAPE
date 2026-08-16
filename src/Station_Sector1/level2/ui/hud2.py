import math
import pygame

class HUD2:
    """Interface Utilisateur ultra-optimisée pour le Niveau 2."""

    def __init__(self):
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)

        # Cadre de batterie
        raw_battery = pygame.image.load('Station_Sector1/level2/battery_frame.png').convert_alpha()
        self.battery_frame = pygame.transform.smoothscale(raw_battery, (170, 55))

        self.color_cyan = (0, 220, 255)
        self.color_green = (50, 255, 120)
        self.color_yellow = (255, 200, 40)
        self.color_red = (255, 60, 60)
        self.color_white = (255, 255, 255)

        self.intro_timer = 180
        self.deposit_flash = 0

        # Surfaces pré-allouées pour soulager le Garbage Collector et la RAM
        self.alert_surface = pygame.Surface((1080, 720), pygame.SRCALPHA)
        self.intro_surface = pygame.Surface((1080, 720), pygame.SRCALPHA)
        
        self.danger_text = self.font_large.render("⚠️ ATTENTION : VÉHICULE NETTOYEUR PROCHE ⚠️", True, self.color_red)
        self.danger_rect = self.danger_text.get_rect(centerx=540, y=78)

        self.intro_t1 = self.font_large.render("TEST BETA : RÉACTEURS SPATIAUX", True, self.color_cyan)
        self.intro_t2 = self.font_medium.render("Alimentez les 2 réacteurs et fuyez par la porte nord", True, self.color_white)

    def trigger_deposit_flash(self):
        self.deposit_flash = 25

    def draw(self, surface, player, reactor_a, reactor_b, exit_open, dist_to_cleaner=1000):
        # 1. Barre de Batterie
        frame_x, frame_y = 20, 15
        surface.blit(self.battery_frame, (frame_x, frame_y))

        ratio = max(0.0, min(1.0, player.battery / player.max_battery))
        bar_w = int(112 * ratio)
        bar_h = 22

        if ratio > 0.5:
            bar_color = self.color_green
        elif ratio > 0.25:
            bar_color = self.color_yellow
        else:
            bar_color = self.color_red

        if bar_w > 0:
            pygame.draw.rect(surface, bar_color, (frame_x + 22, frame_y + 16, bar_w, bar_h), border_radius=3)

        batt_text = self.font_small.render(f"BATTERY: {int(player.battery)}%", True, self.color_white)
        surface.blit(batt_text, (frame_x + 180, frame_y + 20))

        # 2. Panneau d'État des Réacteurs
        panel_w, panel_h = 320, 50
        panel_x = 1080 - panel_w - 20
        panel_y = 15

        p_bg = (15, 20, 35)
        p_border = self.color_green if exit_open else self.color_cyan
        if self.deposit_flash > 0:
            self.deposit_flash -= 1
            p_border = (255, 255, 255)

        pygame.draw.rect(surface, p_bg, (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, p_border, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)

        ra_color = self.color_green if reactor_a.is_full else self.color_cyan
        rb_color = self.color_green if reactor_b.is_full else self.color_cyan

        ra_txt = self.font_small.render(f"RÉACTEUR CENTRAL: {reactor_a.cores}/3", True, ra_color)
        rb_txt = self.font_small.render(f"RÉACTEUR DROIT: {reactor_b.cores}/3", True, rb_color)
        surface.blit(ra_txt, (panel_x + 12, panel_y + 8))
        surface.blit(rb_txt, (panel_x + 12, panel_y + 28))

        # Indicateur boîte portée
        if player.carried_cores > 0:
            carry_bg = pygame.Rect(panel_x, panel_y + panel_h + 8, panel_w, 32)
            pygame.draw.rect(surface, (30, 45, 70), carry_bg, border_radius=6)
            pygame.draw.rect(surface, (255, 220, 50), carry_bg, 2, border_radius=6)
            c_txt = self.font_small.render("📦 BOÎTE PORTÉE : Déposez-la dans un réacteur !", True, (255, 220, 50))
            surface.blit(c_txt, (carry_bg.x + 10, carry_bg.y + 7))

        # 3. Objectif
        if not exit_open:
            obj_str = "OBJECTIF : Récupérez 6 boîtes (3 pour chaque réacteur)"
            obj_color = self.color_cyan
        else:
            obj_str = "⚡ RÉACTEURS ALIMENTÉS : La porte nord est ouverte ! Échappez-vous !"
            obj_color = self.color_green

        obj_surf = self.font_medium.render(obj_str, True, obj_color)
        obj_rect = obj_surf.get_rect(centerx=540, y=28)
        surface.blit(obj_surf, obj_rect)

        # 4. Alerte Nettoyeur
        if dist_to_cleaner < 180:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            alpha = int(pulse * 120)
            self.alert_surface.fill((255, 30, 30, alpha))
            surface.blit(self.alert_surface, (0, 0))
            surface.blit(self.danger_text, self.danger_rect)

        # 5. Intro du Niveau (Fondu)
        if self.intro_timer > 0:
            self.intro_timer -= 1
            alpha = min(255, self.intro_timer * 3)
            self.intro_surface.fill((0, 0, 0, 0))
            self.intro_t1.set_alpha(alpha)
            self.intro_t2.set_alpha(alpha)
            self.intro_surface.blit(self.intro_t1, self.intro_t1.get_rect(centerx=540, centery=320))
            self.intro_surface.blit(self.intro_t2, self.intro_t2.get_rect(centerx=540, centery=370))
            surface.blit(self.intro_surface, (0, 0))
