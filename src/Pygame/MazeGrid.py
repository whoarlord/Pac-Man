from typing import Tuple
from pygame import Surface, display, Rect, font


class MazeGrid:
    def __init__(self, width: int, height: int,
                 window_width: int = 1920, window_height: int = 1020,
                 hud_height: int = 60, margin: int = 5, thick: int = 3,
                 lines_color: Tuple[int, int, int] = (255, 255, 255)):
        self.width = width
        self.height = height
        self.window_width = window_width
        self.window_height = window_height
        self.hud_height = hud_height
        self.maze_height = self.window_height - self.hud_height
        self.margin = margin
        self.thick = thick
        self.lines_color = lines_color
        self.cell_size: Tuple[int, int] = self.calculate_cell_size()

    def reset(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cell_size = self.calculate_cell_size()

    def calculate_cell_size(self) -> Tuple[int, int]:
        cell_width = int((self.window_width - self.margin) / self.width)
        cell_height = int((self.maze_height - self.margin) / self.height)
        return (cell_width, cell_height)

    def get_cell_size(self) -> int:
        return self.cell_size

    def get_lines_color(self) -> Tuple[int, int, int]:
        return self.lines_color

    def get_thick(self) -> int:
        return self.thick

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_window_size(self) -> Tuple[int, int]:
        return (self.window_height, self.window_width)

    def get_increments(self) -> Tuple[int, int]:
        x_increment = int(((self.window_width - self.margin)
                           / self.width))
        y_increment = int(((self.maze_height - self.margin)
                           / self.height))
        return (x_increment, y_increment)

    def get_increments_with_division(self, division: int = 1
                                     ) -> Tuple[int, int]:
        increments = list(self.get_increments())
        return (increments[0] / division, increments[1] / division)

    def calculate_rect_for_cell(self, cell: Tuple[int, int]) -> Rect:
        x_increment = (self.window_width - self.margin) / self.width
        y_increment = (self.maze_height - self.margin) / self.height
        return Rect(cell[0], cell[1], x_increment, y_increment)

    def calculate_pixels_tuple(self, coordinates: Tuple[int, int]
                               ) -> Tuple[int, int]:
        x_increment = (self.window_width - self.margin) / self.width
        y_increment = (self.maze_height - self.margin) / self.height
        return (self.margin + int(x_increment * (coordinates[0])),
                self.margin + int(y_increment * (coordinates[1])))

    def calculate_center(self) -> Tuple[int, int]:
        x = int((self.width - 1) / 2)
        y = int((self.height - 1) / 2)
        return (x, y)
