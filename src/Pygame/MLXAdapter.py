from pygame import (Surface)

Cell = tuple[int, int]


class MLXAdapter:
    def draw_line(self, surface: Surface, source: Cell,
                  target: Cell, color: tuple[int, int, int]) -> None:
        actual_pixel: list[int] = list(source)
        while (actual_pixel != target):
            surface.set_at(actual_pixel, color)
            actual_pixel = self.aproximate_coordinates(actual_pixel, target)
        surface.set_at(actual_pixel, color)

    def draw_cells(self, surface: Surface, cells: list[Cell],
                   color: tuple[int, int, int]) -> None:
        for cell in cells:
            surface.set_at(cell, color)

    def draw_circle(self, surface, color, center, radius):
        cx, cy = center
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    surface.set_at((x, y), color)

    @staticmethod
    def aproximate_integers(source: int, target: int) -> int:
        if (source < target):
            return source + 1
        elif (source > target):
            return source - 1
        return source

    def aproximate_coordinates(self, source: list[int, int],
                               target: Cell
                               ) -> list[int, int]:
        source[0] = self.aproximate_integers(source[0], target[0])
        source[1] = self.aproximate_integers(source[1], target[1])
        return source

    @staticmethod
    def distance(a: Cell, b: Cell) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
