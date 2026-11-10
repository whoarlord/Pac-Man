"""Pixel movement of the Pac-Man entities between cells."""

from src.Game.GameState import GameState
from src.Ui.MazeGrid import MazeGrid
from src.Ui.EntitiesAdapter import EntitiesAdapter
from src.Entities.MovementEntity import MovementEntity, MovingDirection
from src.Entities.Player import Player
from src.Entities.Ghost import Ghost


class MovementController:
    """Moves the entities in pixels towards the cell they are in.

    Attributes:
        game_state: State of the game.
        maze_grid: Grid used to convert cells into pixels.
        entity_adapter: Adapter that gives the images of the entities.
    """

    def __init__(self, game_state: GameState, maze_grid: MazeGrid,
                 entity_adapter: EntitiesAdapter) -> None:
        """Create the controller.

        Args:
            game_state: State of the game.
            maze_grid: Grid used to convert cells into pixels.
            entity_adapter: Adapter that gives the images of the
                entities.
        """

        self.game_state = game_state
        self.maze_grid = maze_grid
        self.entity_adapter = entity_adapter

    def get_blocked_cells(self, ghost: Ghost) -> set[tuple[int, int]]:
        """Return the cells occupied by the other ghosts.

        Args:
            ghost: Ghost that asks. Its own cells are not included.

        Returns:
            A set with the cells occupied by every other ghost.
        """

        blocked: set[tuple[int, int]] = set()
        for other in self.game_state.ghosts:
            if other is not ghost:
                blocked.update(other.get_occupied_cells())
        return blocked

    def calculate_next_movement(self, entity: MovementEntity) -> None:
        """Move the entity one step in pixels towards its cell.

        The step is the size of a cell divided by a number that depends
        on the entity: 5.0 for the player (2.5 with the speed boost),
        15.0 for a scared ghost and 10.0 for the other ghosts. Each step
        is at least 1 pixel and never goes past the cell. For the
        player, it also updates the image for current_direction. When
        the pixel position reaches the cell, current_direction becomes
        NOT_MOVING.

        Args:
            entity: Entity to move.
        """

        division: float = 10.0
        if (isinstance(entity, Player)):
            division = 2.5 if entity.is_speed_boost() else 5.0
            img = self.entity_adapter.makePlayerImage(entity.current_direction)
            entity.set_image(img)
        elif isinstance(entity, Ghost) and entity.is_scared():
            division = 15.0
        x_increment, y_increment = self.maze_grid.get_increments_with_division(
            division)
        target_pixels = self.maze_grid.calculate_pixels_tuple(
            entity.get_coordinates())
        actual_pixels = list(entity.get_pixels())
        if (entity.current_direction == MovingDirection.MOVING_DOWN):
            actual_pixels[1] += y_increment
            if (actual_pixels[1] > target_pixels[1]):
                actual_pixels[1] = target_pixels[1]
        elif (entity.current_direction == MovingDirection.MOVING_UP):
            actual_pixels[1] -= y_increment
            if (actual_pixels[1] < target_pixels[1]):
                actual_pixels[1] = target_pixels[1]
        elif (entity.current_direction == MovingDirection.MOVING_LEFT):
            actual_pixels[0] -= x_increment
            if (actual_pixels[0] < target_pixels[0]):
                actual_pixels[0] = target_pixels[0]
        elif (entity.current_direction == MovingDirection.MOVING_RIGHT):
            actual_pixels[0] += x_increment
            if (actual_pixels[0] > target_pixels[0]):
                actual_pixels[0] = target_pixels[0]
        entity.set_pixels((actual_pixels[0], actual_pixels[1]))
        if (entity.get_pixels() == target_pixels):
            entity.set_current_direction(MovingDirection.NOT_MOVING)
