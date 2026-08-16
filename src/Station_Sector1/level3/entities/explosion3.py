import pygame


class Explosion3(pygame.sprite.Sprite):
    """Explosion plasma lorsqu'un robot ennemi est détruit."""

    DURATION = 24  # frames d'affichage

    def __init__(self, x, y):
        super().__init__()
        raw = pygame.image.load('Station_Sector1/level3/assets/plasma_explosion.png').convert_alpha()
        self.frames = []
        for scale in [0.4, 0.7, 1.0, 0.9, 0.6, 0.3]:
            size = int(48 * scale)
            if size < 4:
                size = 4
            self.frames.append(pygame.transform.smoothscale(raw, (size, size)))

        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(round(x), round(y)))
        self.center_pos = (round(x), round(y))
        self.timer = 0

    def update(self):
        self.timer += 1
        idx = min(int(self.timer / 4), len(self.frames) - 1)
        if idx != self.frame_index:
            self.frame_index = idx
            self.image = self.frames[idx]
            self.rect = self.image.get_rect(center=self.center_pos)

        if self.timer >= self.DURATION:
            self.kill()
