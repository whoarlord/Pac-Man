from typing import Callable
import random


class Pacgum:
    """Pac-Man pac-gum: stores its position and whether it is a super one.

    The position is stored as (x, y), where x is the column and y is
    the row. This class does not know the map: placing and removing
    pac-gums is done outside.
    """

    def __init__(self, x: int, y: int, is_super: bool) -> None:
        """Create a pac-gum at position (x, y).

        is_super is True for a super pac-gum and False for a normal one.
        """

        self.x = x
        self.y = y
        self.is_super = is_super

    @staticmethod
    def get_corner_positions(width: int, height: int) -> list[tuple[int, int]]:
        """Return the four corners of a map of width x height cells.

        The order is top-left, top-right, bottom-left, bottom-right.
        It does not check whether the corners can be stepped on.
        """

        corner1 = (0, 0)
        corner2 = (width - 1, 0)
        corner3 = (0, height - 1)
        corner4 = (width - 1, height - 1)
        return [corner1, corner2, corner3, corner4]

    @staticmethod
    def get_random_positions(width: int, height: int, num_pacgums: int,
                             is_walkable: Callable[[tuple[int, int]], bool],
                             occupied: set[tuple[int, int]]
                             ) -> list[tuple[int, int]]:
        """Return num_pacgums random free positions, without repeats.

        A cell is free if is_walkable(cell) is True and it is not in
        occupied. width and height are the number of columns and rows
        of the map. The set occupied is not modified.

        Raise ValueError if there are fewer free cells than num_pacgums.
        """

        positions: list[tuple[int, int]] = []
        copy_occupied = set(occupied)

        free_cells = 0
        for x in range(width):
            for y in range(height):
                cell = (x, y)
                if is_walkable(cell) and cell not in copy_occupied:
                    free_cells += 1

        if num_pacgums > free_cells:
            raise ValueError(
                f"Cannot place {num_pacgums} pacgums: "
                f"only {free_cells} free cells"
            )

        while len(positions) < num_pacgums:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            cell = (x, y)
            if is_walkable(cell) and cell not in copy_occupied:
                positions.append(cell)
                copy_occupied.add(cell)
        return positions
