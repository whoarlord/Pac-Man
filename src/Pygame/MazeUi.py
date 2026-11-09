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


class MazeUi:
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

    def __init__(self, config: GameConfigModel):
        pygame.init()
        self.config = config
        self.current_level = 0
        self.player: Player
        self.ghosts: list[Ghost] = []
        self.pacgums: list[Pacgum] = []
        self.super_pacgums: list[Pacgum] = []
        self.entity_factory: EntityFactory = EntityFactory()
        self.red_ghost: Ghost | None = None
        self.power_up_timer = 0
        self.POWER_UP_DURATION = 7000
        self.level_timer = 0
        self.paused = False
        self.pause_index = 0
        self.back_to_menu = False
        self.running = True

    def get_actual_level_size(self) -> tuple[int, int]:
        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        return (width, height)

    def get_maze_cell(self, x: int, y: int) -> int:
        return int(self.maze.maze[y][x])

    def get_remaining_time(self) -> int:
        return max(0, self.config.level_max_time
                   - self.level_timer // 1000)

    def initializeMaze(self, width: int, height: int) -> None:
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
        self.current_level = level_index
        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        self.initializeMaze(width, height)
        return (width, height)

    def next_level(self) -> Tuple[int, int] | None:
        if self.current_level + 1 >= len(self.config.levels):
            self.running = False
            return None
        self.player.power_down()
        self.power_up_timer = 0
        self.level_timer = 0
        return self.load_level(self.current_level + 1)

    def scare_ghosts(self) -> None:
        for ghost in self.ghosts:
            if not ghost.is_eaten():
                ghost.scared = True

    def lose_life_and_reset(self) -> None:
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
        if (red_ghost.color == Ghost.GhostColor.RED):
            self.red_ghost = red_ghost

    def get_red_ghost_pos(self) -> tuple[int, int] | None:
        if self.red_ghost is None:
            return None
        return self.red_ghost.get_coordinates()
