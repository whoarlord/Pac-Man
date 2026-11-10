from typing import Tuple
from src.Pygame.MazeGrid import MazeGrid
from src.Pygame.MazeUi import MazeUi
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Entities.MovementEntity import MovingDirection
from src.Entities.Ghost import Ghost
from src.Entities.Pacgums import Pacgum


class LevelLoader:
    def __init__(self, game_state: MazeUi, maze_grid: MazeGrid,
                 entity_adapter: EntitiesAdapter) -> None:
        self.game_state = game_state
        self.maze_grid = maze_grid
        self.entity_adapter = entity_adapter

    def setup_player(self) -> None:
        player_img = self.entity_adapter.makePlayerImage(
            MovingDirection.NOT_MOVING)
        coordinates: Tuple[int, int] = (int((self.maze_grid.width - 1) / 2),
                                        int((self.maze_grid.height - 1) / 2))
        pixels: Tuple[int, int] = self.maze_grid.calculate_pixels_tuple(
            coordinates)
        self.game_state.player = (self.game_state.entity_factory.create_player(
            coordinates, pixels, player_img,
            self.game_state.config.points_per_pacgum,
            self.game_state.config.points_per_super_pacgum,
            self.game_state.config.points_per_ghost,
            self.game_state.config.lives))

    def setup_ghosts(self) -> None:
        ghosts = []
        entity_factory = self.game_state.entity_factory

        red_ghost = self.entity_adapter.makeRedGhostImage()
        coordinates: Tuple[int, int] = (0, 0)
        pixels: Tuple[int, int] = self.maze_grid.calculate_pixels_tuple(
            coordinates)
        red_ghost_entity = entity_factory.create_ghost(
            coordinates, pixels, red_ghost,
            Ghost.GhostColor.RED)
        self.game_state.set_red_ghost(red_ghost_entity)
        ghosts.append(red_ghost_entity)

        yellow_ghost = self.entity_adapter.makeYellowGhostImage()
        coordinates = (0, self.maze_grid.height - 1)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels, yellow_ghost,
                                        Ghost.GhostColor.YELLOW)
        )

        blue_ghost = self.entity_adapter.makeBlueGhostImage()
        coordinates = (self.maze_grid.width - 1, 0)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels, blue_ghost,
                                        Ghost.GhostColor.BLUE)
        )

        pink_ghost = self.entity_adapter.makePinkGhostImage()
        coordinates = (self.maze_grid.width - 1, self.maze_grid.height - 1)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels,
                                        pink_ghost,
                                        Ghost.GhostColor.PINK))

        self.game_state.ghosts = ghosts

    def setup_pacgums(self) -> None:
        self.game_state.pacgums = []
        self.game_state.super_pacgums = []
        entity_factory = self.game_state.entity_factory
        width = self.maze_grid.get_width()
        height = self.maze_grid.get_height()
        corners = Pacgum.get_corner_positions(width, height)
        center = (int((width - 1) / 2), int((height - 1) / 2))
        occupied = set(corners)
        occupied.add(center)

        free_cells = 0
        for x in range(width):
            for y in range(height):
                cell = (x, y)
                if self.game_state.is_walkable(cell) and cell not in occupied:
                    free_cells += 1
        pacgum_ratio = self.game_state.config.PACGUM_RATIO
        if self.game_state.config.pacgum is None:
            amount = int(free_cells * pacgum_ratio)
        else:
            amount = min(self.game_state.config.pacgum, free_cells)
        positions = Pacgum.get_random_positions(width, height,
                                                amount,
                                                self.game_state.is_walkable,
                                                occupied)

        for x, y in corners:
            self.game_state.super_pacgums.append(entity_factory.create_pacgum(
                x, y, True))
        for x, y in positions:
            self.game_state.pacgums.append(entity_factory.create_pacgum(
                x, y, False))

    def reset_player_position(self) -> None:
        self.game_state.player.x = int((self.maze_grid.width - 1) / 2)
        self.game_state.player.y = int((self.maze_grid.height - 1) / 2)
        px_jugador = self.maze_grid.calculate_pixels_tuple(
            (self.game_state.player.x, self.game_state.player.y))
        self.game_state.player.set_pixels(px_jugador)
        self.game_state.player.set_current_direction(
            MovingDirection.NOT_MOVING)
        self.game_state.player.desired_direction = MovingDirection.NOT_MOVING

    def initialize_level(self) -> None:
        self.entity_adapter.resize(self.maze_grid.get_cell_size())
        self.game_state.player.set_image(self.entity_adapter.makePlayerImage(
            MovingDirection.NOT_MOVING))
        self.reset_player_position()
        self.setup_ghosts()
        self.setup_pacgums()

    def load_first_level(self) -> None:
        maze_size = self.game_state.load_level(0)
        width, height = maze_size
        self.maze_grid.reset(width, height)
        self.initialize_level()

    def load_level(self) -> None:
        maze_size = self.game_state.next_level()
        if (maze_size is None):
            return
        width, height = maze_size
        self.maze_grid.reset(width, height)
        self.initialize_level()

    def setup_entities(self) -> None:
        self.game_state.initializeMaze(self.maze_grid.width,
                                       self.maze_grid.height)
        self.setup_player()
