from src.Pygame.MazeUi import MazeUi
from src.Pygame.MazeGrid import MazeGrid
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Entities.MovementEntity import MovementEntity, MovingDirection
from src.Entities.Player import Player
from src.Entities.Ghost import Ghost


class MovementController:
    def __init__(self, game_state: MazeUi, maze_grid: MazeGrid,
                 entity_adapter: EntitiesAdapter) -> None:
        self.game_state = game_state
        self.maze_grid = maze_grid
        self.entity_adapter = entity_adapter

    def get_blocked_cells(self, ghost: Ghost) -> set[tuple[int, int]]:
        blocked: set[tuple[int, int]] = set()
        for other in self.game_state.ghosts:
            if other is not ghost:
                blocked.update(other.get_occupied_cells())
        return blocked

    def calculate_next_movement(self, entity: MovementEntity) -> None:
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
