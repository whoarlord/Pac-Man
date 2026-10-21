from src.Entities.MovementEntity import MovementEntity
from typing import Callable
from collections import deque
from enum import Enum
from pygame import Surface


class Ghost(MovementEntity):
    """Pac-Man ghost: chases the player or runs away from it.

    Which of the two to use depends on player.is_powered_up, and that
    is checked outside this class.
    The ghost does not know the map: it receives an is_walkable function
    that says whether a cell can be stepped on (not a wall and inside
    the map). Distances to the player are computed with BFS.
    """
    class GhostColor(Enum):
        RED = 'red'
        YELLOW = 'yellow'
        BLUE = 'blue'
        PINK = 'pink'

    def __init__(self, x: int, y: int, image: Surface | None,
                 color: GhostColor) -> None:
        """Create a ghost at position (x, y)."""

        super().__init__(x, y, image)
        self.color = color

    def set_image(self, image: Surface):
        self.image = image

    def _get_neighbors(self, cell: tuple[int, int],
                       can_move: Callable[[tuple[int, int], tuple[int, int]],
                                          bool]) -> list[tuple[int, int]]:
        """Return the walkable cells next to cell.

        The cells are checked in the order up, down, left, right, and the
        result keeps that order. Cells for which is_walkable returns False
        (walls or outside the map) are left out.
        """

        x, y = cell
        up = (x, y - 1)
        down = (x, y + 1)
        left = (x - 1, y)
        right = (x + 1, y)
        candidates = [up, down, left, right]
        result = []
        for candidate in candidates:
            if can_move(cell, candidate):
                result.append(candidate)
        return result

    def _get_distances(self, start: tuple[int, int],
                       can_move: Callable[[tuple[int, int], tuple[int, int]],
                                          bool]) -> dict[tuple[int, int], int]:
        """Return the number of steps from start to every reachable cell.

        It uses BFS: cells are explored in rings, first the ones 1 step
        away, then 2 steps away, and so on. That is why the first time a
        cell is reached is always by the shortest path. Cells that cannot
        be reached are not in the result.
        """

        # distances also works as the record of already visited cells.
        distances = {start: 0}
        # queue holds the cells whose neighbours are still to be checked.
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in self._get_neighbors(current, can_move):
                if neighbor not in distances:
                    # Only a cell seen for the first time gets a distance.
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _choose_cell(self, player_pos: tuple[int, int],
                     can_move: Callable[[tuple[int, int], tuple[int, int]],
                                        bool], chase: bool) -> tuple[int, int]:
        """Return the neighbouring cell the ghost should move to.

        It computes the distance from player_pos to every cell and looks
        at the ghost's walkable neighbours. If chase is True it picks the
        one with the smallest distance, otherwise the one with the
        largest. On a tie, the first one in the order up, down, left,
        right wins. It does not move the ghost.

        It assumes the ghost has at least one walkable neighbour and that
        all of them can be reached from player_pos.
        """

        distances = self._get_distances(player_pos, can_move)
        neighbors = self._get_neighbors((self.x, self.y), can_move)
        best = neighbors[0]
        for cell in neighbors:
            # Strict < and > keep the first cell when there is a tie.
            if chase and distances[cell] < distances[best]:
                best = cell
            elif not chase and distances[cell] > distances[best]:
                best = cell
        return best

    def _move_to(self, cell: tuple[int, int]) -> None:
        """Move the ghost to cell, which must be one of its 4 neighbours.

        If cell is not next to the ghost, nothing happens.
        """

        # Compare cell with where each move would take the ghost.
        if cell == self.next_pos_up():
            self.move_up()
        elif cell == self.next_pos_down():
            self.move_down()
        elif cell == self.next_pos_left():
            self.move_left()
        elif cell == self.next_pos_right():
            self.move_right()

    # To agree with partner: how is_walkable reaches the ghost
    # (it must also return False for cells outside the map), and whether
    # catch_player and run_from_player move the ghost, as they do now, or
    # return the direction instead.

    def catch_player(self, player_pos: tuple[int, int],
                     can_move: Callable[[tuple[int, int], tuple[int, int]],
                                        bool]) -> None:
        """Move the ghost one cell along the shortest path to the player.

        player_pos is the player's position as (x, y). is_walkable says
        whether a cell can be stepped on.
        """

        cell = self._choose_cell(player_pos, can_move, True)
        self._move_to(cell)

    def run_from_player(self, player_pos: tuple[int, int],
                        can_move: Callable[[tuple[int, int], tuple[int, int]],
                                           bool]) -> None:
        """Move the ghost one cell away from the player.

        It goes to the neighbouring cell with the longest path to
        player_pos, given as (x, y). is_walkable says whether a cell can
        be stepped on.
        """

        cell = self._choose_cell(player_pos, can_move, False)
        self._move_to(cell)


if __name__ == "__main__":
    # Test map (5 columns x 3 rows). The cells marked with # are closed
    # off: they are surrounded by walls, so nobody can enter them.
    #
    #    x: 0 1 2 3 4
    # y=0   . . . . .
    # y=1   . . # . .
    # y=2   . . # . .
    #
    # Each wall is stored once, as a pair of neighbouring cells.
    walls = {
        ((2, 0), (2, 1)), ((1, 1), (2, 1)), ((2, 1), (3, 1)),
        ((2, 1), (2, 2)), ((1, 2), (2, 2)), ((2, 2), (3, 2)),
    }

    def can_move(origin: tuple[int, int], target: tuple[int, int]) -> bool:
        """Fake map: False if a wall is in the way or target is outside."""

        x, y = target
        if x < 0 or x > 4 or y < 0 or y > 2:
            return False
        if (origin, target) in walls or (target, origin) in walls:
            return False
        return True

    color = Ghost.GhostColor.RED
    ghost = Ghost(0, 1, color)

    # _get_neighbors: walls and cells outside the map are left out.
    tests = [
        ((1, 1), [(1, 0), (1, 2), (0, 1)]),
        ((0, 0), [(0, 1), (1, 0)]),
        ((3, 1), [(3, 0), (3, 2), (4, 1)]),
        ((4, 2), [(4, 1), (3, 2)]),
    ]

    for cell, expected in tests:
        result = ghost._get_neighbors(cell, can_move)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} cell={cell} result={result} expected={expected}")

    # _get_distances: BFS from the player at (4, 1).
    expected_distances = {
        (4, 1): 0, (4, 0): 1, (4, 2): 1, (3, 1): 1,
        (3, 0): 2, (3, 2): 2, (2, 0): 3, (1, 0): 4,
        (0, 0): 5, (1, 1): 5, (0, 1): 6, (1, 2): 6,
        (0, 2): 7,
    }
    distances = ghost._get_distances((4, 1), can_move)
    status = "OK" if distances == expected_distances else "FAIL"
    print(f"{status} distances={distances}")

    # _choose_cell: closest or farthest neighbour, ties go to the first.
    choose_tests = [
        ((0, 1), True, (0, 0)),
        ((0, 1), False, (0, 2)),
        ((1, 1), True, (1, 0)),
        ((1, 1), False, (1, 2)),
    ]

    for pos, chase, expected in choose_tests:
        g = Ghost(pos[0], pos[1], color)
        result = g._choose_cell((4, 1), can_move, chase)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} ghost={pos} chase={chase} "
              f"result={result} expected={expected}")

    # _move_to: one test for each direction.
    move_tests = [
        ((1, 1), (1, 0)),
        ((1, 1), (1, 2)),
        ((1, 1), (0, 1)),
        ((3, 1), (4, 1)),
    ]

    for start, cell in move_tests:
        g = Ghost(start[0], start[1], color)
        g._move_to(cell)
        result = (g.x, g.y)
        status = "OK" if result == cell else "FAIL"
        print(f"{status} start={start} cell={cell} result={result}")

    # catch_player and run_from_player: one step each.
    g = Ghost(0, 1, color)
    g.catch_player((4, 1), can_move)
    status = "OK" if (g.x, g.y) == (0, 0) else "FAIL"
    print(f"{status} catch one step: {(g.x, g.y)} expected (0, 0)")

    g = Ghost(0, 1, color)
    g.run_from_player((4, 1), can_move)
    status = "OK" if (g.x, g.y) == (0, 2) else "FAIL"
    print(f"{status} run one step: {(g.x, g.y)} expected (0, 2)")

    # catch_player six times in a row: the ghost goes around the wall.
    g = Ghost(0, 1, color)
    path = []
    for _ in range(6):
        g.catch_player((4, 1), can_move)
        path.append((g.x, g.y))
    expected_path = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (4, 1)]
    status = "OK" if path == expected_path else "FAIL"
    print(f"{status} path={path}")

    # A wall between two normal cells: (3, 0) and (3, 1) are both free,
    # but now they are not connected, so the ghost must go through (4, 0).
    walls.add(((3, 0), (3, 1)))
    g = Ghost(0, 1, color)
    path = []
    for _ in range(6):
        g.catch_player((4, 1), can_move)
        path.append((g.x, g.y))
    expected_path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1)]
    status = "OK" if path == expected_path else "FAIL"
    print(f"{status} wall between normal cells: path={path}")
