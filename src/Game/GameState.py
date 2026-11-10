"""State of the Pac-Man game: entities, maze, timers and input events."""

import pygame
import sys
try:
    from mazegenerator import MazeGenerator
except ImportError:
    print("Error: the 'mazegenerator' package is not installed. "
          "Install it first (make install).", file=sys.stderr)
    sys.exit(1)
from .. import (EntityFactory, Ghost, Player, MovingDirection)
from ..Entities.Pacgums import Pacgum
from ..Config.ConfigParser import GameConfigModel
from typing import Tuple, Callable


class GameState:
    """Holds the state of the game and the rules to move on the maze.

    It stores the player, the ghosts, the pacgums, the timers and the
    maze of the current level, and it reads the keyboard events.

    Attributes:
        KEY_DIRECTIONS: Maps each movement key (arrows and WASD) to its
            MovingDirection.
        config: Configuration of the game.
        current_level: Index of the current level.
        player: Player of the game.
        ghosts: Ghosts of the game.
        pacgums: Normal pacgums that are still in the level.
        super_pacgums: Super pacgums that are still in the level.
        entity_factory: Factory used to create the entities.
        red_ghost: Red ghost, or None if it has not been set.
        power_up_timer: Time since the power-up started, in
            milliseconds.
        POWER_UP_DURATION: Duration of the power-up, in milliseconds.
        RESPAWN_DELAY: Time an eaten ghost waits to come back, in
            milliseconds.
        level_timer: Time spent in the current level, in milliseconds.
        paused: True if the game is paused.
        pause_index: Index of the selected option of the pause menu.
        pause_options: Texts of the options of the pause menu.
        back_to_menu: True if the player chose to go back to the main
            menu.
        running: True while the game is running.
        maze_width: Number of columns of the maze.
        maze_height: Number of rows of the maze.
        maze: Maze of the current level. It is created by
            initializeMaze, so it does not exist before a level is
            loaded.
    """

    KEY_DIRECTIONS = {
        pygame.K_UP: MovingDirection.MOVING_UP,
        pygame.K_w: MovingDirection.MOVING_UP,
        pygame.K_DOWN: MovingDirection.MOVING_DOWN,
        pygame.K_s: MovingDirection.MOVING_DOWN,
        pygame.K_LEFT: MovingDirection.MOVING_LEFT,
        pygame.K_a: MovingDirection.MOVING_LEFT,
        pygame.K_RIGHT: MovingDirection.MOVING_RIGHT,
        pygame.K_d: MovingDirection.MOVING_RIGHT,
    }

    def __init__(self, config: GameConfigModel) -> None:
        """Initialize pygame and create an empty game state.

        Args:
            config: Configuration of the game.
        """

        pygame.init()
        self.config = config
        self.current_level = 0
        self.player: Player
        self.ghosts: list[Ghost] = []
        self.pacgums: list[Pacgum] = []
        self.super_pacgums: list[Pacgum] = []
        self.entity_factory: EntityFactory = EntityFactory()
        self.entity_factory.set_can_move(self.can_move)
        self.entity_factory.set_available_cell(self.available_cell)
        self.red_ghost: Ghost | None = None
        self.power_up_timer = 0
        self.POWER_UP_DURATION = 7000
        self.RESPAWN_DELAY = 5000
        self.level_timer = 0
        self.paused = False
        self.pause_index = 0
        self.pause_options = ["Resume", "Return to Main Menu"]
        self.back_to_menu = False
        self.running = True
        self.maze_width = 0
        self.maze_height = 0

    def get_actual_level_size(self) -> tuple[int, int]:
        """Return the size of the current level.

        Returns:
            A tuple (width, height) in cells.
        """

        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        return (width, height)

    def get_maze_cell(self, x: int, y: int) -> int:
        """Return the value of a cell of the maze.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            The value of the cell, which encodes its walls.
        """

        return int(self.maze.maze[y][x])

    def get_remaining_time(self) -> int:
        """Return the time left to finish the level.

        Returns:
            The remaining time in seconds, never below 0.
        """

        return max(0, self.config.level_max_time
                   - self.level_timer // 1000)

    def initializeMaze(self, width: int, height: int) -> None:
        """Generate a new maze and store its size.

        The configured seed is used in the first level, and 0 in the
        rest. The program exits if the maze cannot be generated.

        Args:
            width: Number of columns of the maze.
            height: Number of rows of the maze.

        Raises:
            SystemExit: If the maze generator fails.
        """

        self.maze_width = width
        self.maze_height = height
        seed = self.config.seed if self.current_level == 0 else 0
        try:
            self.maze: MazeGenerator = MazeGenerator((width, height),
                                                     perfect=False, seed=seed)
        except Exception as e:
            print(f"Error: The maze generator could not create the map of "
                  f"{width}x{height} ({e}).", file=sys.stderr)
            pygame.quit()
            sys.exit(1)

    def load_level(self, level_index: int) -> Tuple[int, int]:
        """Make a level the current one and generate its maze.

        Args:
            level_index: Index of the level in the configuration.

        Returns:
            A tuple (width, height) with the size of the level.
        """

        self.current_level = level_index
        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        self.initializeMaze(width, height)
        return (width, height)

    def next_level(self) -> Tuple[int, int] | None:
        """Move to the next level.

        The power-up and the level timers are reset. If there are no
        more levels, the game stops running.

        Returns:
            A tuple (width, height) with the size of the new level, or
            None if there are no more levels.
        """

        if self.current_level + 1 >= len(self.config.levels):
            self.running = False
            return None
        self.player.power_down()
        self.power_up_timer = 0
        self.level_timer = 0
        return self.load_level(self.current_level + 1)

    def scare_ghosts(self) -> None:
        """Make every ghost that is not eaten scared."""

        for ghost in self.ghosts:
            if not ghost.is_eaten():
                ghost.scared = True

    def lose_life_and_reset(self) -> None:
        """Take a life from the player and send the ghosts back.

        The player is powered down and the power-up timer is reset. If
        the player has no lives left, the game stops running. Otherwise,
        every ghost respawns and stops being scared or eaten.
        """

        self.player.lose_life()
        self.player.power_down()
        self.power_up_timer = 0
        if self.player.lives <= 0:
            self.running = False
            return
        for ghost in self.ghosts:
            ghost.respawn()
            ghost.respawn_timer = 0
            ghost.scared = False

    def bind_events(self, handle_pause: Callable[[int], None]
                    ) -> dict[str, bool]:
        """Read the pygame events and apply them to the game.

        Keys: ESC or P pauses the game, the arrows and WASD set the
        desired direction of the player, I toggles invincibility, V adds
        a life, B toggles the speed boost, L asks to skip the level and
        F toggles the ghost freeze. While the game is paused, the keys
        are given to handle_pause.

        Args:
            handle_pause: Function that receives the key pressed while
                the game is paused.

        Returns:
            A dictionary with the keys 'extra_life' and 'level_skip',
            which are True if the animation of that event is needed.
        """

        result: dict[str, bool] = {'extra_life': False,
                                   'level_skip': False}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.paused:
                    handle_pause(event.key)
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.paused = True
                    self.pause_index = 0
                elif event.key in self.KEY_DIRECTIONS:
                    self.player.desired_direction = self.KEY_DIRECTIONS[
                        event.key]
                elif event.key == pygame.K_i:
                    self.player.change_invincibility()
                elif event.key == pygame.K_v:
                    self.player.add_extra_life()
                    result.update({'extra_life': True})
                elif event.key == pygame.K_b:
                    self.player.change_speed_boost()
                elif event.key == pygame.K_l:
                    result.update({'level_skip': True})
                elif event.key == pygame.K_f:
                    self.player.change_ghost_freeze()
        return result

    def set_red_ghost(self, red_ghost: Ghost) -> None:
        """Store the red ghost.

        Nothing happens if the ghost is not red.

        Args:
            red_ghost: Ghost to store.
        """

        if (red_ghost.color == Ghost.GhostColor.RED):
            self.red_ghost = red_ghost

    def get_red_ghost_pos(self) -> tuple[int, int] | None:
        """Return the cell of the red ghost.

        Returns:
            A tuple (x, y), or None if the red ghost has not been set.
        """

        if self.red_ghost is None:
            return None
        return self.red_ghost.get_coordinates()

    def can_move(self, origin: tuple[int, int],
                 target: tuple[int, int]) -> bool:
        """Tell whether an entity can go from a cell to a next one.

        The move is not allowed if the target is outside the maze, if it
        is not next to the origin, or if there is a wall between them.

        Args:
            origin: Cell as (x, y) where the entity is.
            target: Cell as (x, y) where the entity wants to go.

        Returns:
            True if the move is allowed, False otherwise.
        """

        x_target, y_target = target
        if (x_target < 0 or x_target >= self.maze_width or y_target < 0
                or y_target >= self.maze_height):
            return False
        x_origin, y_origin = origin
        actual_cell = self.get_maze_cell(x_origin, y_origin)
        dx = x_target - x_origin
        dy = y_target - y_origin
        if dx == 0 and dy == -1:
            wall = 1
        elif dx == 1 and dy == 0:
            wall = 2
        elif dx == 0 and dy == 1:
            wall = 4
        elif dx == -1 and dy == 0:
            wall = 8
        else:
            return False
        return bool((actual_cell & wall) == 0)

    def available_cell(self, target: tuple[int, int]) -> bool:
        """Tell whether a cell is inside the maze.

        Args:
            target: Cell as (x, y) to check.

        Returns:
            True if the cell is inside the maze, False otherwise.
        """

        x_target, y_target = target
        if (x_target < 0 or x_target >= self.maze_width or y_target < 0
                or y_target >= self.maze_height):
            return False
        return True

    def is_walkable(self, cell: tuple[int, int]) -> bool:
        """Tell whether a cell can be stepped on.

        A cell can be stepped on if it is inside the maze and it is not
        closed by walls on its four sides (value 15).

        Args:
            cell: Cell as (x, y) to check.

        Returns:
            True if the cell can be stepped on, False otherwise.
        """

        x, y = cell
        if not (0 <= x < self.maze_width and 0 <= y < self.maze_height):
            return False
        return bool(self.get_maze_cell(x, y) != 15)
