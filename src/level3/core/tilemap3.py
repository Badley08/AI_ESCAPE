import json
import pygame


class TileMap3:
    """Carte de tuiles du Niveau 3 (arène de combat 104x58, tile 16px)."""

    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        self.tile_size = data.get('tile_size', 16)
        grid_dim = data.get('grid_dim', [104, 58])
        self.cols = grid_dim[0]
        self.rows = grid_dim[1]
        self.map_width = self.cols * self.tile_size
        self.map_height = self.rows * self.tile_size

        # Grille 2D pré-allouée (True = praticable)
        self.grid = [[True] * self.cols for _ in range(self.rows)]
        self.wall_rects = []

        for t in data['tiles']:
            c, r = t['col'], t['row']
            if 0 <= r < self.rows and 0 <= c < self.cols:
                walkable = t.get('walkable', True)
                self.grid[r][c] = walkable
                if not walkable:
                    self.wall_rects.append(
                        pygame.Rect(c * self.tile_size, r * self.tile_size,
                                    self.tile_size, self.tile_size)
                    )

        # Cache spatial pour collisions rapides (cellules de 64px)
        self._cell_size = 64
        self._spatial = {}
        for wr in self.wall_rects:
            for cx in range(wr.left // self._cell_size, wr.right // self._cell_size + 1):
                for cy in range(wr.top // self._cell_size, wr.bottom // self._cell_size + 1):
                    self._spatial.setdefault((cx, cy), []).append(wr)

    def get_colliding_walls(self, rect):
        """Retourne les murs en collision potentielle avec le rect donné."""
        results = []
        seen = set()
        cs = self._cell_size
        for cx in range(rect.left // cs, rect.right // cs + 1):
            for cy in range(rect.top // cs, rect.bottom // cs + 1):
                for w in self._spatial.get((cx, cy), ()):
                    wid = id(w)
                    if wid not in seen:
                        seen.add(wid)
                        results.append(w)
        return results

    def is_walkable(self, px, py):
        """Vérifie si une position en pixels est praticable."""
        c = int(px) // self.tile_size
        r = int(py) // self.tile_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return False

    def is_rect_clear(self, rect):
        """Vérifie qu'un rect ne chevauche aucun mur."""
        for w in self.get_colliding_walls(rect):
            if rect.colliderect(w):
                return False
        return True
