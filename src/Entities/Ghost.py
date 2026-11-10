"""Ghost entity of the Pac-Man game and its chasing behaviour."""

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

    Attributes:
        MAX_WAIT_TICKS: Ticks a ghost waits when its best cell is
            blocked by another ghost before taking another route.
        CLYDE_DISTANCE: Distance under which the yellow ghost retreats.
        CLYDE_MARGIN: Extra distance the yellow ghost must gain before
            it stops retreating.
        available_cell: Function that tells whether a cell can be
            stepped on.
        color: Color of the ghost, which decides how it chases.
        spawn_x: Column where the ghost respawns.
        spawn_y: Row where the ghost respawns.
        respawn_timer: Remaining time before the ghost comes back. It
            is greater than 0 while the ghost is eaten.
        scared: True if the ghost is running away from the player.
        home_x: Column of the ghost's home cell.
        home_y: Row of the ghost's home cell.
        wait_ticks: Ticks the ghost has been waiting for a blocked cell.
        retreating: True if the yellow ghost is going back home.
    """

    class GhostColor(Enum):
        """Colors of the ghosts, each one with its own behaviour.

        Attributes:
            RED: Chases the player directly.
            YELLOW: Chases the player but retreats when it is close.
            BLUE: Aims at a cell based on the player and the red ghost.
            PINK: Aims at a cell ahead of the player.
        """

        RED = 'red'
        YELLOW = 'yellow'
        BLUE = 'blue'
        PINK = 'pink'

    MAX_WAIT_TICKS = 12
    CLYDE_DISTANCE = 8
    CLYDE_MARGIN = 3

    def __init__(self, x: int, y: int, x_pixel: int,
                 y_pixel: int, image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool],
                 color: GhostColor,
                 available_cell: Callable[[tuple[int, int]], bool]) -> None:
        """Create a ghost at position (x, y).

        The starting cell is also used as the spawn and home cell.

        Args:
            x: Starting column of the ghost.
            y: Starting row of the ghost.
            x_pixel: Starting horizontal position in pixels.
            y_pixel: Starting vertical position in pixels.
            image: Surface used to draw the ghost.
            can_move: Function that receives the current cell and the
                target cell, and returns True if the move is allowed.
            color: Color of the ghost.
            available_cell: Function that receives a cell and returns
                True if it can be stepped on.
        """

        super().__init__(x, y, x_pixel, y_pixel, image, can_move)
        self.available_cell = available_cell
        self.color = color
        self.spawn_x = x
        self.spawn_y = y
        self.respawn_timer = 0
        self.scared = False
        self.home_x = x
        self.home_y = y
        self.wait_ticks = 0
        self.retreating = False

    def get_home_coordinates(self) -> tuple[int, int]:
        """Return the home cell of the ghost.

        Returns:
            A tuple (x, y) with the column and the row of the home.
        """

        return (self.home_x, self.home_y)

    def set_image(self, image: Surface) -> None:
        """Change the image used to draw the ghost.

        Args:
            image: New surface for the ghost.
        """

        self.image = image

    def respawn(self) -> None:
        """Move the ghost back to its spawn cell."""

        self.x = self.spawn_x
        self.y = self.spawn_y

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        """Return the cells the ghost is occupying.

        Besides its own cell, it includes the cell it just left, which
        is the one behind it according to current_direction.

        Returns:
            A set with one or two (x, y) cells.
        """

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
        result keeps that order. Cells for which can_move returns False
        (walls or outside the map) are left out.

        Args:
            cell: Cell as (x, y) whose neighbours are wanted.

        Returns:
            A list with the walkable neighbour cells.
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

        Args:
            start: Cell as (x, y) where the search starts.

        Returns:
            A dictionary that maps each reachable cell to its distance
            from start. The distance of start is 0.
        """

        distances = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in self._get_neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _get_distance_to_actual_cell(self, start: tuple[int, int],
                                     player_pos: tuple[int, int]) -> int:
        """Return the number of steps from start to player_pos.

        It uses BFS and stops as soon as player_pos is found.

        Args:
            start: Cell as (x, y) where the search starts.
            player_pos: Cell as (x, y) of the player.

        Returns:
            The length of the shortest path. If player_pos cannot be
            reached, it returns the distance of the last explored cell
            plus 1.
        """

        distances = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in self._get_neighbors(current):
                if neighbor == player_pos:
                    return distances[current] + 1
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances[current] + 1

    def _best_neighbor(self, distances: dict[tuple[int, int], int],
                       candidates: list[tuple[int, int]], chase: bool
                       ) -> tuple[int, int] | None:
        """Choose the best cell among the candidates.

        Args:
            distances: Distance from each cell to the target, as
                returned by _get_distances.
            candidates: Cells to choose from.
            chase: If True, the cell closest to the target is chosen.
                If False, the farthest one is chosen.

        Returns:
            The best cell, or None if no candidate is in distances.
            With a tie, the first candidate in the list is kept.
        """

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
                     blocked: set[tuple[int, int]] | None
                     ) -> tuple[int, int]:
        """Choose the next cell for the ghost.

        If the best cell is blocked (for example by another ghost), the
        ghost waits up to MAX_WAIT_TICKS ticks and then takes the best
        free cell instead.

        Args:
            player_pos: Cell as (x, y) the ghost goes towards or away
                from.
            chase: True to get closer to player_pos, False to get
                away from it.
            blocked: Cells that cannot be used, or None if there are
                none.

        Returns:
            The chosen cell. It is the ghost's own cell if it has to
            stay where it is.
        """

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
        If cell is not next to the ghost, nothing happens. It also
        updates current_direction.

        Args:
            cell: Neighbour cell as (x, y) to move to.
        """

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

    def target_for_pink(self, player_pos: tuple[int, int],
                        player_direction: MovingDirection
                        ) -> tuple[int, int]:
        """Return the target cell of the pink ghost.

        It aims at a cell ahead of the player, trying 4 cells first and
        then fewer, until it finds one that can be stepped on.

        Args:
            player_pos: Cell as (x, y) of the player.
            player_direction: Direction the player is moving in.

        Returns:
            The target cell, or player_pos if no cell ahead is valid.
        """

        target_cell = None
        movement: int = 4
        while (target_cell is None):
            target_cell = MovementEntity.next_pos_to_target(player_pos,
                                                            player_direction,
                                                            movement)
            if (not self.available_cell(target_cell)):
                target_cell = None
            movement -= 1
            if (movement == 0):
                return player_pos
        return target_cell

    def target_for_blue(self, player_pos: tuple[int, int],
                        red_position: tuple[int, int],
                        player_direction: MovingDirection
                        ) -> tuple[int, int]:
        """Return the target cell of the blue ghost.

        It takes the cell 2 steps ahead of the player and extends the
        line from the red ghost through that cell, doubling its length.

        Args:
            player_pos: Cell as (x, y) of the player.
            red_position: Cell as (x, y) of the red ghost.
            player_direction: Direction the player is moving in.

        Returns:
            The target cell, or player_pos if that cell cannot be
            stepped on.
        """

        target_cell = None
        intermediate_target_cell = MovementEntity.next_pos_to_target(
            player_pos,
            player_direction,
            2)
        target_cell = self.extend_line(intermediate_target_cell,
                                       red_position)
        if (not self.available_cell(target_cell)):
            target_cell = player_pos
        return target_cell

    def target_for_yellow(self, player_pos: tuple[int, int]) -> None:
        """Update the retreating state of the yellow ghost.

        The ghost starts retreating when it is closer than
        CLYDE_DISTANCE to the player, and stops when it is farther than
        CLYDE_DISTANCE + CLYDE_MARGIN.

        Args:
            player_pos: Cell as (x, y) of the player.
        """

        distance = self._get_distance_to_actual_cell(self.get_coordinates(),
                                                     player_pos)
        if self.retreating:
            if distance > self.CLYDE_DISTANCE + self.CLYDE_MARGIN:
                self.retreating = False
        elif distance < self.CLYDE_DISTANCE:
            self.retreating = True

    @staticmethod
    def extend_line(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        """Extend the line from b through a by its own length.

        Args:
            a: Cell as (x, y) the line goes through.
            b: Cell as (x, y) where the line starts.

        Returns:
            The cell a + (a - b).
        """

        dx, dy = a[0] - b[0], a[1] - b[1]
        return (a[0] + dx, a[1] + dy)

    def catch_player(self, player_pos: tuple[int, int],
                     player_direction: MovingDirection,
                     blocked: set[tuple[int, int]] | None = None,
                     red_position: tuple[int, int] | None = None
                     ) -> None:
        """Move the ghost one cell along the shortest path to the player.

        The target depends on the color of the ghost. The yellow ghost
        goes home instead while it is retreating.

        Args:
            player_pos: Cell as (x, y) of the player.
            player_direction: Direction the player is moving in.
            blocked: Cells that cannot be used, such as the ones
                occupied by other ghosts.
            red_position: Cell as (x, y) of the red ghost. Only the
                blue ghost uses it; without it, blue chases the
                player directly.
        """

        target_cell: tuple[int, int] = player_pos
        if (self.color == self.GhostColor.RED):
            target_cell = player_pos
        elif (self.color == self.GhostColor.PINK):
            target_cell = self.target_for_pink(player_pos, player_direction)
        elif (self.color == self.GhostColor.BLUE):
            if red_position is not None:
                target_cell = self.target_for_blue(player_pos, red_position,
                                                   player_direction)
            else:
                target_cell = player_pos
        elif (self.color == self.GhostColor.YELLOW):
            self.target_for_yellow(player_pos)
            if (self.retreating):
                self.run_to_home(blocked)
                return
        target_cell = self._choose_cell(target_cell, True, blocked)
        self._move_to(target_cell)

    def run_to_home(self, blocked: set[tuple[int, int]] | None = None) -> None:
        """Move the ghost one cell along the shortest path to its home.

        Args:
            blocked: Cells that cannot be used, such as the ones
                occupied by other ghosts.
        """

        cell = self._choose_cell(self.get_home_coordinates(), True, blocked)
        self._move_to(cell)

    def is_eaten(self) -> bool:
        """Tell whether the ghost has been eaten.

        Returns:
            True if respawn_timer is greater than 0, False otherwise.
        """

        return self.respawn_timer > 0

    def is_scared(self) -> bool:
        """Tell whether the ghost is scared of the player.

        Returns:
            True if the ghost is scared, False otherwise.
        """

        return self.scared
