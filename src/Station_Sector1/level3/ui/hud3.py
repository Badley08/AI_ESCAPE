import math
import pygame


class HUD3:
    """Interface du Niveau 3 : batterie, vague, terminaux, ennemis restants."""

    def __init__(self):
        self.font_big = pygame.font.Font(None, 32)
        self.font_med = pygame.font.Font(None, 24)
        self.font_sm = pygame.font.Font(None, 20)

        # Surfaces pré-allouées
        self.bar_bg = pygame.Surface((200, 16), pygame.SRCALPHA)
        self.bar_bg.fill((30, 30, 40, 180))

        self.panel_bg = pygame.Surface((220, 120), pygame.SRCALPHA)
        self.panel_bg.fill((10, 10, 18, 160))

        self.warning_flash = 0

        # Crosshair pré-rendu
        self.crosshair_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.crosshair_surf, (0, 220, 255, 180), (12, 12), 10, 2)
        pygame.draw.line(self.crosshair_surf, (0, 220, 255, 120), (12, 2), (12, 8), 1)
        pygame.draw.line(self.crosshair_surf, (0, 220, 255, 120), (12, 16), (12, 22), 1)
        pygame.draw.line(self.crosshair_surf, (0, 220, 255, 120), (2, 12), (8, 12), 1)
        pygame.draw.line(self.crosshair_surf, (0, 220, 255, 120), (16, 12), (22, 12), 1)

    def draw(self, surface, player, wave, max_waves, enemies_alive, terminals_activated,
             total_terminals, mouse_pos):
        # Panneau HUD en haut à gauche
        surface.blit(self.panel_bg, (8, 8))

        # Batterie
        bat_label = self.font_med.render("BATTERIE", True, (0, 200, 255))
        surface.blit(bat_label, (16, 14))

        bar_x, bar_y = 16, 36
        surface.blit(self.bar_bg, (bar_x, bar_y))
        fill_w = int(200 * max(0, player.battery) / player.max_battery)
        if player.battery > 50:
            color = (0, 220, 100)
        elif player.battery > 25:
            color = (255, 180, 0)
        else:
            color = (255, 50, 50)
            self.warning_flash += 1
        pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, 16))
        pct = self.font_sm.render(f"{int(player.battery)}%", True, (255, 255, 255))
        surface.blit(pct, (bar_x + 200 + 6, bar_y - 1))

        # Vague
        wave_txt = self.font_med.render(f"VAGUE {wave}/{max_waves}", True, (255, 200, 50))
        surface.blit(wave_txt, (16, 58))

        # Ennemis restants
        enemy_txt = self.font_sm.render(f"Ennemis: {enemies_alive}", True, (255, 100, 100))
        surface.blit(enemy_txt, (16, 80))

        # Terminaux
        term_color = (0, 255, 120) if terminals_activated >= total_terminals else (180, 180, 200)
        term_txt = self.font_med.render(
            f"GÉNÉRATEURS {terminals_activated}/{total_terminals}", True, term_color)
        surface.blit(term_txt, (16, 100))

        # Crosshair à la position de la souris
        surface.blit(self.crosshair_surf, (mouse_pos[0] - 12, mouse_pos[1] - 12))

        # Alerte batterie basse
        if player.battery < 20 and self.warning_flash % 40 < 20:
            warn = self.font_big.render("⚠ BATTERIE CRITIQUE", True, (255, 50, 50))
            surface.blit(warn, warn.get_rect(centerx=540, centery=680))
