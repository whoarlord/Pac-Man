import pygame
from mazegenerator import MazeGenerator
from .EntitiesAdapter import EntitiesAdapter
from .. import (EntityFactory, Ghost, Player, MovementEntity,
                MovingDirection)
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
        self.entity_factory: EntityFactory
        self.power_up_timer = 0
        self.POWER_UP_DURATION = 7000
        self.level_timer = 0
        self.paused = False
        self.pause_index = 0
        self.back_to_menu = False
        self.running = True

    def get_actual_level_size(self):
        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        return (width, height)

    def reset(self, width: int, height: int):
        self.initializeMaze(width, height)
        self.ghosts = []
        self.pacgums = []
        self.super_pacgums = []

        self.power_up_timer = 0
        self.level_timer = 0
        self.paused = False
        self.pause_index = 0
        self.back_to_menu = False

    def get_maze_cell(self, x: int, y: int):
        return self.maze.maze[y][x]

    def get_remaining_time(self):
        return max(0, self.config.level_max_time
                   - self.level_timer // 1000)

    def saveImage(self, image: pygame.Surface, name: str) -> None:
        pygame.image.save(image, name)

    def initializeMaze(self, width: int, height: int) -> None:
        seed = self.config.seed if self.current_level == 0 else 0
        self.maze: MazeGenerator = MazeGenerator((width, height),
                                                 perfect=False, seed=seed)

    """ def createAllSquaresAndSavingThem(self, x_limit: int) -> None:
        x = 5
        y = 5
        increment = 50
        margin = 10
        for i in range(16):
            self.createMazeBlock(i, x, y, x + increment, y + increment)

            zone = self.screen.subsurface(
                pygame.Rect(x, y, increment + 1, increment + 1)
            ).copy()
            self.saveImage(zone, f"../img/square_{i}.png")
            x += increment + margin
            if (x + increment + margin > x_limit):
                x = 5
                y += increment + margin """

    def load_level(self, level_index: int) -> Tuple[int, int]:
        self.current_level = level_index
        width = self.config.levels[self.current_level].width
        height = self.config.levels[self.current_level].height
        self.initializeMaze(width, height)
        self.player.power_down()
        self.power_up_timer = 0
        self.level_timer = 0
        return (width, height)

    def next_level(self) -> Tuple[int, int] | None:
        if self.current_level + 1 >= len(self.config.levels):
            self.running = False
            return None
        return self.load_level(self.current_level + 1)

    def bind_events(self, handle_pause: Callable[int, None]) -> None:
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
