import math
import pygame

class DataBox(pygame.sprite.Sprite):
    """Boîte de données à récupérer et apporter aux réacteurs."""

    def __init__(self, x, y):
        super().__init__()
        raw_img = pygame.image.load('level2/data_fragment.png').convert_alpha()
        self.image = pygame.transform.smoothscale(raw_img, (32, 32))

        self.base_x = float(x)
        self.base_y = float(y)
        self.rect = self.image.get_rect(center=(int(self.base_x), int(self.base_y)))
        self.timer = float(x + y)

    def update(self):
        self.timer += 0.07
        offset_y = math.sin(self.timer) * 4.0
        self.rect.center = (int(self.base_x), int(self.base_y + offset_y))
