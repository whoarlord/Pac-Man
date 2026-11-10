"""Grid of the Pac-Man window: size and position of the cells."""

from typing import Tuple
from pygame import Rect


class MazeGrid:
    """Computes the size and position of the cells of the maze.

    The cells are squares as big as possible so that the maze fits in
    the area between the top margin and the HUD, centered in the window.

    Attributes:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        window_width: Width of the window in pixels.
        window_height: Height of the window in pixels.
        hud_height: Height in pixels of the HUD, at the bottom.
        margin_top_height: Height in pixels of the area above the maze.
        maze_height: Height in pixels available for the maze.
        margin: Pixels left free around the maze.
        thick: Thickness in pixels of the walls.
        lines_color: Color of the walls.
        cell_size: Size in pixels (width, height) of a cell. It is
            always a square.
        offset_x: Pixel column of the left side of the maze.
        offset_y: Pixel row of the top side of the maze.
    """

    def __init__(self, width: int, height: int,
                 window_width: int = 1920, window_height: int = 1080,
                 hud_height: int = 60, margin: int = 5,
                 margin_top_height: int = 60, thick: int = 3,
                 lines_color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Create the grid and compute the size of the cells.

        Args:
            width: Number of columns of the maze.
            height: Number of rows of the maze.
            window_width: Width of the window in pixels.
            window_height: Height of the window in pixels.
            hud_height: Height in pixels of the HUD.
            margin: Pixels left free around the maze.
            margin_top_height: Height in pixels of the area above the
                maze.
            thick: Thickness in pixels of the walls.
            lines_color: Color of the walls.
        """

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
        """Change the size of the maze and compute the cells again.

        Args:
            width: New number of columns.
            height: New number of rows.
        """

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

    def get_cell_size(self) -> tuple[int, int]:
        """Return the size in pixels of a cell as (width, height)."""

        return self.cell_size

    def get_lines_color(self) -> Tuple[int, int, int]:
        """Return the color of the walls."""

        return self.lines_color

    def get_thick(self) -> int:
        """Return the thickness in pixels of the walls."""

        return self.thick

    def get_width(self) -> int:
        """Return the number of columns of the maze."""

        return self.width

    def get_height(self) -> int:
        """Return the number of rows of the maze."""

        return self.height

    def get_window_size(self) -> Tuple[int, int]:
        """Return the size of the window as (width, height) in pixels."""

        return (self.window_width, self.window_height)

    def get_increments(self) -> Tuple[int, int]:
        """Return the pixels of a whole cell on each axis.

        Returns:
            A tuple (x_increment, y_increment).
        """

        return (self.cell_size[0], self.cell_size[1])

    def get_increments_with_division(self, division: float = 1.0
                                     ) -> Tuple[int, int]:
        """Return the increments of a cell divided by a number.

        Args:
            division: Number to divide by.

        Returns:
            A tuple (x_increment, y_increment) of integers, each one at
            least 1.
        """

        increments = self.get_increments()
        return (max(1, int(increments[0] / division)),
                max(1, int(increments[1] / division)))

    def calculate_rect_for_cell(self, cell: Tuple[int, int]) -> Rect:
        """Return a rectangle with the size of a cell.

        Args:
            cell: Top-left corner of the rectangle as (x, y) in pixels,
                not the coordinates of a cell.

        Returns:
            The rectangle.
        """

        return Rect(cell[0], cell[1], self.cell_size[0], self.cell_size[1])

    def calculate_pixels_tuple(self, coordinates: Tuple[int, int]
                               ) -> Tuple[int, int]:
        """Return the pixel position of the top-left corner of a cell.

        Args:
            coordinates: Cell as (x, y).

        Returns:
            A tuple (x_pixel, y_pixel).
        """

        pixel_x = self.offset_x + (coordinates[0] * self.cell_size[0])
        pixel_y = self.offset_y + (coordinates[1] * self.cell_size[1])
        return (pixel_x, pixel_y)

    def calculate_center(self) -> Tuple[int, int]:
        """Return the center cell of the maze as (x, y)."""

        x = int((self.width - 1) / 2)
        y = int((self.height - 1) / 2)
        return (x, y)

    def calculate_center_pixels(self) -> Tuple[int, int]:
        """Return the center of the window (not of the maze) in pixels."""

        center_x = self.window_width // 2
        center_y = self.window_height // 2
        return (center_x, center_y)
