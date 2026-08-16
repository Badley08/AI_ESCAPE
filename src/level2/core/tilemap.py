import json
import pygame
from collections import deque

class TileMap:
    """Gestionnaire de carte avec collisions strictes et pathfinding BFS complet garanti sans traversée de murs."""

    def __init__(self, json_path='level2/level2_grid.json'):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.tile_size = data.get('tile_size', 16)
        self.cols = data['grid_dim']['cols']
        self.rows = data['grid_dim']['rows']
        self.map_width = self.cols * self.tile_size
        self.map_height = self.rows * self.tile_size

        # Grille 2D pré-allouée
        self.grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.wall_rects_map = {}

        for tile in data['tiles']:
            c, r = tile['col'], tile['row']
            walkable = tile['walkable']
            self.grid[r][c] = walkable
            if not walkable:
                self.wall_rects_map[(c, r)] = pygame.Rect(
                    c * self.tile_size,
                    r * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )

        self._cached_wall_list = []

    def is_walkable(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.grid[row][col]
        return False

    def get_colliding_walls(self, rect):
        """Retourne tous les rectangles des murs en collision potentielle avec le rect."""
        min_c = max(0, rect.left // self.tile_size)
        max_c = min(self.cols - 1, rect.right // self.tile_size)
        min_r = max(0, rect.top // self.tile_size)
        max_r = min(self.rows - 1, rect.bottom // self.tile_size)

        self._cached_wall_list.clear()
        for r in range(min_r, max_r + 1):
            row_data = self.grid[r]
            for c in range(min_c, max_c + 1):
                if not row_data[c]:
                    w = self.wall_rects_map.get((c, r))
                    if w:
                        self._cached_wall_list.append(w)
        return self._cached_wall_list

    def get_path(self, start_pos, target_pos):
        """BFS exhaustif sur les couloirs praticables — ne traverse JAMAIS un mur."""
        start_c = max(0, min(self.cols - 1, int(start_pos[0] // self.tile_size)))
        start_r = max(0, min(self.rows - 1, int(start_pos[1] // self.tile_size)))
        target_c = max(0, min(self.cols - 1, int(target_pos[0] // self.tile_size)))
        target_r = max(0, min(self.rows - 1, int(target_pos[1] // self.tile_size)))

        # Si la cible est sur un mur, chercher la case praticable la plus proche
        if not self.grid[target_r][target_c]:
            best_dist = 999999
            best_t = (target_c, target_r)
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nc, nr = target_c + dc, target_r + dr
                    if 0 <= nc < self.cols and 0 <= nr < self.rows and self.grid[nr][nc]:
                        d = dc * dc + dr * dr
                        if d < best_dist:
                            best_dist = d
                            best_t = (nc, nr)
            target_c, target_r = best_t

        if (start_c, start_r) == (target_c, target_r):
            return []

        queue = deque([(start_c, start_r)])
        came_from = {(start_c, start_r): None}
        closest_tile = (start_c, start_r)
        min_target_dist = (start_c - target_c) ** 2 + (start_r - target_r) ** 2

        found = False
        while queue:
            curr = queue.popleft()
            if curr == (target_c, target_r):
                found = True
                break

            d = (curr[0] - target_c) ** 2 + (curr[1] - target_r) ** 2
            if d < min_target_dist:
                min_target_dist = d
                closest_tile = curr

            for dc, dr in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nc, nr = curr[0] + dc, curr[1] + dr
                if 0 <= nc < self.cols and 0 <= nr < self.rows and self.grid[nr][nc]:
                    if (nc, nr) not in came_from:
                        came_from[(nc, nr)] = curr
                        queue.append((nc, nr))

        end_node = (target_c, target_r) if found else closest_tile
        if end_node == (start_c, start_r):
            return []

        # Reconstitution du chemin tile par tile
        path = []
        curr = end_node
        half_tile = self.tile_size // 2
        while curr != (start_c, start_r) and curr is not None:
            path.append((
                curr[0] * self.tile_size + half_tile,
                curr[1] * self.tile_size + half_tile
            ))
            curr = came_from.get(curr)

        path.reverse()
        return path
