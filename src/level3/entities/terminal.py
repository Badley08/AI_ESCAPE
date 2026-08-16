import pygame
import math


class Terminal(pygame.sprite.Sprite):
    """Générateur d'urgence à surcharger (maintenir E pendant ~3 secondes)."""

    ACTIVATION_TIME = 180  # 3 secondes à 60 FPS
    INTERACT_RANGE = 60

    def __init__(self, x, y, terminal_id):
        super().__init__()
        self.terminal_id = terminal_id

        raw = pygame.image.load('level3/assets/generator_terminal.png').convert_alpha()
        self.base_image = pygame.transform.smoothscale(raw, (50, 50))
        self.image = self.base_image.copy()

        self.x = float(x)
        self.y = float(y)
        self.rect = self.image.get_rect(center=(round(x), round(y)))

        self.activated = False
        self.progress = 0  # 0 à ACTIVATION_TIME
        self.glow_timer = 0

        # Texte pré-rendu
        self.font = pygame.font.Font(None, 18)

    def try_activate(self, player_x, player_y, holding_e):
        """Appelé chaque frame. Progresse si E est maintenu à proximité."""
        if self.activated:
            return False

        dist = math.hypot(player_x - self.x, player_y - self.y)
        if dist < self.INTERACT_RANGE and holding_e:
            self.progress += 1
            if self.progress >= self.ACTIVATION_TIME:
                self.activated = True
                return True  # Vient d'être activé
        else:
            # Régression lente si on s'éloigne
            self.progress = max(0, self.progress - 1)
        return False

    def update(self):
        self.glow_timer += 1

    def draw(self, surface, offset_x, offset_y):
        sx = round(self.x) + offset_x
        sy = round(self.y) + offset_y

        # Dessin du terminal
        surface.blit(self.image, (sx - 25, sy - 25))

        if self.activated:
            # Lueur pulsante verte
            pulse = abs(math.sin(self.glow_timer * 0.06))
            glow_r = int(28 + pulse * 8)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 255, 120, int(40 + pulse * 40)),
                               (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (sx - glow_r, sy - glow_r))

            label = self.font.render("ACTIVÉ", True, (0, 255, 120))
            surface.blit(label, label.get_rect(centerx=sx, top=sy + 28))
        else:
            # Barre de progression
            if self.progress > 0:
                bar_w = 40
                bar_h = 5
                bx = sx - bar_w // 2
                by = sy + 30
                pygame.draw.rect(surface, (60, 60, 60), (bx, by, bar_w, bar_h))
                fill = int(bar_w * self.progress / self.ACTIVATION_TIME)
                pygame.draw.rect(surface, (0, 200, 255), (bx, by, fill, bar_h))

            # Indicateur "Appuyez E"
            dist_label = self.font.render("[E]", True, (180, 180, 200))
            surface.blit(dist_label, dist_label.get_rect(centerx=sx, top=sy + 28))
