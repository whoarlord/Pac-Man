from typing import Tuple
from pygame import Rect


class MazeGrid:
    def __init__(self, width: int, height: int,
                 window_width: int = 1920, window_height: int = 1080,
                 hud_height: int = 60, margin: int = 5,
                 margin_top_height: int = 60, thick: int = 3,
                 lines_color: Tuple[int, int, int] = (255, 255, 255)):
        self.width = width
        self.height = height
        self.window_width = window_width
        self.window_height = window_height
        self.hud_height = hud_height
        self.margin_top_height = margin_top_height
        self.maze_height = (self.window_height - self.hud_height
                            - self.margin_top_height)
        self.margin = margin
        self.thick = thick
        self.lines_color = lines_color

        ideal_width = int((self.window_width - (self.margin * 2)) /
                          self.width)
        ideal_height = int((self.maze_height - (self.margin * 2)) /
                           self.height)
        square_size = min(ideal_width, ideal_height)
        self.cell_size: Tuple[int, int] = (square_size, square_size)

        self.offset_x = (self.window_width - (square_size * self.width)) // 2
        self.offset_y = (self.margin_top_height +
                         (self.maze_height - (square_size * self.height)) // 2)

    def reset(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        ideal_width = int((self.window_width - (self.margin * 2)) / self.width)
        ideal_height = int((self.maze_height - (self.margin * 2)) /
                           self.height)
        square_size = min(ideal_width, ideal_height)
        self.cell_size = (square_size, square_size)

        self.offset_x = (self.window_width - (square_size * self.width)) // 2
        self.offset_y = self.margin_top_height + (
            self.maze_height - (square_size * self.height)) // 2

    """ def calculate_cell_size(self) -> Tuple[int, int]:
        ideal_width = int((self.window_width - self.margin) / self.width)
        ideal_height = int((self.maze_height - self.margin) / self.height)
        square_size = min(ideal_width, ideal_height)
        return (square_size, square_size) """

    def get_cell_size(self) -> tuple[int, int]:
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
        return (self.window_width, self.window_height)

    def get_increments(self) -> Tuple[int, int]:
        return (self.cell_size[0], self.cell_size[1])

    def get_increments_with_division(self, division: float = 1.0
                                     ) -> Tuple[int, int]:
        increments = self.get_increments()
        return (max(1, int(increments[0] / division)),
                max(1, int(increments[1] / division)))

    def calculate_rect_for_cell(self, cell: Tuple[int, int]) -> Rect:
        return Rect(cell[0], cell[1], self.cell_size[0], self.cell_size[1])

    def calculate_pixels_tuple(self, coordinates: Tuple[int, int]
                               ) -> Tuple[int, int]:
        pixel_x = self.offset_x + (coordinates[0] * self.cell_size[0])
        pixel_y = self.offset_y + (coordinates[1] * self.cell_size[1])
        return (pixel_x, pixel_y)

    def calculate_center(self) -> Tuple[int, int]:
        x = int((self.width - 1) / 2)
        y = int((self.height - 1) / 2)
        return (x, y)

    def calculate_center_pixels(self) -> Tuple[int, int]:
        center_x = self.window_width // 2
        center_y = self.window_height // 2
        return (center_x, center_y)
