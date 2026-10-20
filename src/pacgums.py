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


if __name__ == "__main__":
    # Test map (5 columns x 3 rows):
    #
    #    x: 0 1 2 3 4
    # y=0   . . . . .
    # y=1   . . . . .
    # y=2   . . . . .
    corners = Pacgum.get_corner_positions(5, 3)
    expected = [(0, 0), (4, 0), (0, 2), (4, 2)]
    status = "OK" if corners == expected else "FAIL"
    print(f"{status} 5x3 corners={corners} expected={expected}")

    # Another size, to check that it does not only work for 5x3.
    corners = Pacgum.get_corner_positions(10, 7)
    expected = [(0, 0), (9, 0), (0, 6), (9, 6)]
    status = "OK" if corners == expected else "FAIL"
    print(f"{status} 10x7 corners={corners} expected={expected}")

    # Test map for get_random_positions (5 columns x 3 rows), # is a wall:
    #
    #    x: 0 1 2 3 4
    # y=0   . . . . .
    # y=1   . . # . .
    # y=2   . . # . .
    walls = {(2, 1), (2, 2)}

    def is_walkable(cell: tuple[int, int]) -> bool:
        """Fake map: False for walls and for cells outside the grid."""

        x, y = cell
        if cell in walls:
            return False
        if x < 0 or x > 4 or y < 0 or y > 2:
            return False
        return True

    occupied = {(0, 0), (4, 1)}
    free_cells = {
        (1, 0), (2, 0), (3, 0), (4, 0),
        (0, 1), (1, 1), (3, 1),
        (0, 2), (1, 2), (3, 2), (4, 2),
    }

    # The result is random, so the check is repeated many times.
    all_ok = True
    for _ in range(200):
        positions = Pacgum.get_random_positions(
            5, 3, 5, is_walkable, occupied)
        if len(positions) != 5:
            all_ok = False
        if len(set(positions)) != len(positions):
            all_ok = False
        for cell in positions:
            if cell not in free_cells:
                all_ok = False
    status = "OK" if all_ok else "FAIL"
    print(f"{status} 5 pacgums: right amount, no repeats, only free cells")

    # Asking for exactly as many pacgums as free cells: all of them.
    positions = Pacgum.get_random_positions(
        5, 3, 11, is_walkable, occupied)
    all_ok = len(positions) == 11 and set(positions) == free_cells
    status = "OK" if all_ok else "FAIL"
    print(f"{status} 11 pacgums: every free cell used exactly once")

    # Asking for one more than the free cells: it must raise ValueError.
    try:
        Pacgum.get_random_positions(5, 3, 12, is_walkable, occupied)
        print("FAIL 12 pacgums: no ValueError raised")
    except ValueError as error:
        print(f"OK 12 pacgums: ValueError raised ({error})")

    # Asking for 0 pacgums: empty list.
    positions = Pacgum.get_random_positions(5, 3, 0, is_walkable, occupied)
    status = "OK" if positions == [] else "FAIL"
    print(f"{status} 0 pacgums: positions={positions}")

    # The occupied set given by the caller must not be modified.
    status = "OK" if occupied == {(0, 0), (4, 1)} else "FAIL"
    print(f"{status} occupied unchanged: {occupied}")
