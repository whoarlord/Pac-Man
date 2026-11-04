from src.Entities.MovementEntity import MovementEntity, MovingDirection
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

    MAX_WAIT_TICKS = 12

    def __init__(self, x: int, y: int, x_pixel: int,
                 y_pixel: int, image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool],
                 color: GhostColor) -> None:
        """Create a ghost at position (x, y)."""

        super().__init__(x, y, x_pixel, y_pixel, image, can_move)
        self.color = color
        self.spawn_x = x
        self.spawn_y = y
        self.respawn_timer = 0
        self.scared = False
        self.wait_ticks = 0

    def set_image(self, image: Surface) -> None:
        self.image = image

    def respawn(self) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        cells = {(self.x, self.y)}
        if self.current_direction == MovingDirection.MOVING_UP:
            cells.add((self.x, self.y + 1))
        elif self.current_direction == MovingDirection.MOVING_DOWN:
            cells.add((self.x, self.y - 1))
        elif self.current_direction == MovingDirection.MOVING_LEFT:
            cells.add((self.x + 1, self.y))
        elif self.current_direction == MovingDirection.MOVING_RIGHT:
            cells.add((self.x - 1, self.y))
        return cells

    def _get_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
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
            if self.can_move(cell, candidate):
                result.append(candidate)
        return result

    def _get_distances(self, start: tuple[int, int]
                       ) -> dict[tuple[int, int], int]:
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
            for neighbor in self._get_neighbors(current):
                if neighbor not in distances:
                    # Only a cell seen for the first time gets a distance.
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _best_neighbor(self, distances: dict[tuple[int, int], int],
                       candidates: list[tuple[int, int]], chase: bool
                       ) -> tuple[int, int] | None:
        best: tuple[int, int] | None = None
        best_dist = 0
        for cell in candidates:
            if cell not in distances:
                continue
            cell_dist = distances[cell]
            if best is None:
                better = True
            elif chase:
                better = cell_dist < best_dist
            else:
                better = cell_dist > best_dist
            if better:
                best = cell
                best_dist = cell_dist
        return best

    def _choose_cell(self, player_pos: tuple[int, int], chase: bool,
                     blocked: set[tuple[int, int]] | None = None
                     ) -> tuple[int, int]:
        if blocked is None:
            blocked = set()
        distances = self._get_distances(player_pos)
        neighbors = self._get_neighbors((self.x, self.y))
        best = self._best_neighbor(distances, neighbors, chase)
        if best is None:
            return (self.x, self.y)
        if best not in blocked:
            self.wait_ticks = 0
            return best
        self.wait_ticks += 1
        if self.wait_ticks <= self.MAX_WAIT_TICKS:
            return (self.x, self.y)
        self.wait_ticks = 0
        free = []
        for cell in neighbors:
            if cell not in blocked:
                free.append(cell)
        alternative = self._best_neighbor(distances, free, chase)
        if alternative is None:
            return (self.x, self.y)
        return alternative

    def _move_to(self, cell: tuple[int, int]) -> None:
        """Move the ghost to cell, which must be one of its 4 neighbours.

        If cell is not next to the ghost, nothing happens.
        """

        # Compare cell with where each move would take the ghost.
        if cell == self.next_pos_up():
            self.move_up()
            self.current_direction = MovingDirection.MOVING_UP
        elif cell == self.next_pos_down():
            self.move_down()
            self.current_direction = MovingDirection.MOVING_DOWN
        elif cell == self.next_pos_left():
            self.move_left()
            self.current_direction = MovingDirection.MOVING_LEFT
        elif cell == self.next_pos_right():
            self.move_right()
            self.current_direction = MovingDirection.MOVING_RIGHT

    # To agree with partner: how is_walkable reaches the ghost
    # (it must also return False for cells outside the map), and whether
    # catch_player and run_from_player move the ghost, as they do now, or
    # return the direction instead.

    def catch_player(self, player_pos: tuple[int, int],
                     blocked: set[tuple[int, int]] | None = None) -> None:
        """Move the ghost one cell along the shortest path to the player.

        player_pos is the player's position as (x, y). is_walkable says
        whether a cell can be stepped on.
        """

        cell = self._choose_cell(player_pos, True, blocked)
        self._move_to(cell)

    def run_from_player(self, player_pos: tuple[int, int],
                        blocked: set[tuple[int, int]] | None = None
                        ) -> None:
        """Move the ghost one cell away from the player.

        It goes to the neighbouring cell with the longest path to
        player_pos, given as (x, y). is_walkable says whether a cell can
        be stepped on.
        """

        cell = self._choose_cell(player_pos, False, blocked)
        self._move_to(cell)

    def is_eaten(self) -> bool:
        return self.respawn_timer > 0

    def is_scared(self) -> bool:
        return self.scared
