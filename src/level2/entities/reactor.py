import math
import pygame

class Reactor:
    """Réacteur circulaire ultra-optimisé (polices pré-chargées)."""

    def __init__(self, name, x, y, max_cores=3):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.radius = 42
        self.cores = 0
        self.max_cores = max_cores
        self.rect = pygame.Rect(int(x - self.radius), int(y - self.radius), self.radius * 2, self.radius * 2)
        
        # Police pré-allouée à l'initialisation (zéro lag mémoire)
        self.font = pygame.font.Font(None, 22)
        self._update_text()

    def _update_text(self):
        self.rendered_text = self.font.render(
            f"{self.name}: {self.cores}/{self.max_cores}",
            True,
            (255, 255, 255)
        )

    @property
    def is_full(self):
        return self.cores >= self.max_cores

    def deposit_core(self):
        if not self.is_full:
            self.cores += 1
            self._update_text()
            return True
        return False

    def draw(self, surface, offset_x, offset_y):
        screen_x = int(self.x + offset_x)
        screen_y = int(self.y + offset_y)

        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        
        if self.is_full:
            color = (50, 255, 120)
            glow_radius = int(self.radius + pulse * 6)
        else:
            color = (0, 200, 255)
            glow_radius = int(self.radius + pulse * 4)

        pygame.draw.circle(surface, color, (screen_x, screen_y), glow_radius, 2)
        pygame.draw.circle(surface, (*color, 35), (screen_x, screen_y), self.radius)
        surface.blit(self.rendered_text, self.rendered_text.get_rect(center=(screen_x, screen_y)))
