import pygame
from mazegenerator import MazeGenerator
from .EntitiesAdapter import EntitiesAdapter
from .. import (EntityFactory, Ghost, Player, MovementEntity,
                MovingDirection)
from ..Entities.Pacgums import Pacgum
from ..Config.ConfigParser import GameConfigModel
from typing import Tuple


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
        self.font = pygame.font.Font(None, 40)
        self.config = config
        self.current_level = 0
        self.width = config.levels[self.current_level].width
        self.height = config.levels[self.current_level].height
        self.window_width = 1920
        self.window_height = 1080
        self.hud_height = 60
        self.maze_height = self.window_height - self.hud_height
        self.margin = 5
        self.thick = 3
        self.lines_color = (255, 255, 255)
        self.cell_size: Tuple[float, float] = self.calculate_cell_size()
        self.initializeMaze()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.window_width, self.window_height))
        self.screen.fill("black")
        self.player: Player
        self.ghosts: list[Ghost] = []
        self.pacgums: list[Pacgum] = []
        self.super_pacgums: list[Pacgum] = []
        self.entity_factory: EntityFactory
        self.entity_adapter: EntitiesAdapter
        self.power_up_timer = 0
        self.POWER_UP_DURATION = 7000
        self.level_timer = 0

    def load_level(self, level_index: int) -> None:
        self.current_level = level_index
        self.width = self.config.levels[self.current_level].width
        self.height = self.config.levels[self.current_level].height
        self.cell_size = self.calculate_cell_size()
        self.initializeMaze()

    def calculate_cell_size(self) -> Tuple[float, float]:
        cell_width = (self.window_width - self.margin) / self.width
        cell_height = (self.maze_height - self.margin) / self.height
        return (cell_width, cell_height)

    def saveImage(self, image: pygame.Surface, name: str) -> None:
        pygame.image.save(image, name)

    def createRect(self, init_x: float, init_y: float, finish_x: float,
                   finish_y: float, N: bool, E: bool, W: bool,
                   S: bool) -> None:
        if (N):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, init_y),
                             (finish_x, init_y), self.thick)
        if (E):
            pygame.draw.line(self.screen, self.lines_color,
                             (finish_x, init_y),
                             (finish_x, finish_y), self.thick)
        if (W):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, init_y),
                             (init_x, finish_y), self.thick)
        if (S):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, finish_y),
                             (finish_x, finish_y), self.thick)

    def createMazeBlock(self, cell: int, x: int, y: int,
                        x_increment: int, y_increment: int) -> None:
        N = bool(cell & 1)
        E = bool(cell & 2)
        S = bool(cell & 4)
        W = bool(cell & 8)
        self.createRect(x, y, x + x_increment, y + y_increment, N, E, W, S)

    def makeMaze(self, x_cells: int, y_cells: int) -> None:
        x = self.margin
        y = self.margin
        x_increment = (self.window_width - self.margin) // x_cells
        y_increment = (self.maze_height - self.margin) // y_cells
        for i in range(y_cells):
            for j in range(x_cells):
                actual_cell = self.maze.maze[i][j]
                self.createMazeBlock(actual_cell, x, y,
                                     x_increment, y_increment)
                x += x_increment
            x = self.margin
            y += y_increment

    def initializeMaze(self) -> None:
        seed = self.config.seed if self.current_level == 0 else 0
        self.maze: MazeGenerator = MazeGenerator((self.width, self.height),
                                                 perfect=False, seed=seed)

    def createAllSquaresAndSavingThem(self, x_limit: int) -> None:
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
                y += increment + margin

    def place_player(self, player: pygame.Surface) -> None:
        x = int((self.width - 1) / 2)
        y = int((self.height - 1) / 2)
        self.place_element(player, self.calculate_pixels_tuple((x, y)))

    def place_element(self, element: pygame.Surface,
                      coordinates: Tuple[int, int]) -> None:
        self.screen.blit(element, self.calculate_rect_for_cell(coordinates))

    def calculate_rect_for_cell(self, cell: Tuple[int, int]) -> pygame.Rect:
        x_increment = (self.window_width - self.margin) / self.width
        y_increment = (self.maze_height - self.margin) / self.height
        return pygame.Rect(cell[0], cell[1], x_increment,
                           y_increment)

    def can_move(self, origin: tuple[int, int],
                 target: tuple[int, int]) -> bool:
        x_target, y_target = target
        if (x_target < 0 or x_target >= self.width or y_target < 0
                or y_target >= self.height):
            return False
        x_origin, y_origin = origin
        actual_cell = self.maze.maze[y_origin][x_origin]
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

    def draw_hud(self) -> None:
        remaining = max(0, self.config.level_max_time
                        - self.level_timer // 1000)
        texts = [
            f"Score: {self.player.score}",
            f"Lives: {self.player.lives}",
            f"Level: {self.current_level + 1}",
            f"Time: {remaining}"
        ]
        for i, text in enumerate(texts):
            image = self.font.render(text, True, (255, 255, 255))
            x = 20 + i * (self.window_width // 4)
            y = self.maze_height + (self.hud_height - image.get_height()) // 2
            self.screen.blit(image, (x, y))

    def print_map(self) -> None:
        self.screen.fill("black")
        self.makeMaze(self.width, self.height)
        self.draw_pacgums()
        self.place_element(self.player.image,
                           (self.player.get_pixels()))
        for ghost in self.ghosts:
            self.place_element(ghost.image,
                               ghost.get_pixels())
        self.draw_hud()
        self.check_collisions()

    def calculate_pixels_tuple(self, coordinates: Tuple[int, int]
                               ) -> Tuple[int, int]:
        x_increment = (self.window_width - self.margin) / self.width
        y_increment = (self.maze_height - self.margin) / self.height
        return (self.margin + int(x_increment * (coordinates[0])),
                self.margin + int(y_increment * (coordinates[1])))

    def calculate_next_movement(self, entity: MovementEntity) -> None:
        division: int = 10
        if (isinstance(entity, Player)):
            division = 5
            img = self.entity_adapter.makePlayerImage(entity.current_direction)
            entity.set_image(img)
        x_increment = int(((self.window_width - self.margin)
                           / self.width) / division)
        y_increment = int(((self.maze_height - self.margin)
                           / self.height) / division)
        target_pixels = self.calculate_pixels_tuple(entity.get_coordinates())
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

    def next_level(self) -> None:
        if self.current_level + 1 >= len(self.config.levels):
            self.running = False
            return
        self.load_level(self.current_level + 1)
        self.entity_adapter = EntitiesAdapter((int(self.cell_size[0]),
                                               int(self.cell_size[1])))
        self.player.set_image(self.entity_adapter.makePlayerImage(
            MovingDirection.NOT_MOVING))
        self.reset_player_position()
        self.player.power_down()
        self.power_up_timer = 0
        self.level_timer = 0
        self.setup_ghosts(self.entity_adapter, self.entity_factory)
        self.setup_pacgums(self.entity_factory)

    def setup_player(self, entityAdapter: EntitiesAdapter,
                     entityFactory: EntityFactory) -> None:
        player = entityAdapter.makePlayerImage(MovingDirection.NOT_MOVING)
        coordinates: Tuple[int, int] = (int((self.width - 1) / 2),
                                        int((self.height - 1) / 2))
        pixels: Tuple[int, int] = self.calculate_pixels_tuple(coordinates)
        self.place_player(player)
        self.player = (entityFactory.
                       create_player(coordinates, pixels,
                                     player, self.can_move,
                                     self.config.points_per_pacgum,
                                     self.config.points_per_super_pacgum,
                                     self.config.points_per_ghost,
                                     self.config.lives))

    def setup_ghosts(self, entityAdapter: EntitiesAdapter,
                     entityFactory: EntityFactory) -> None:
        self.ghosts = []
        red_ghost = entityAdapter.makeRedGhostImage()
        coordinates: Tuple[int, int] = (0, 0)
        pixels: Tuple[int, int] = self.calculate_pixels_tuple(coordinates)
        self.place_element(red_ghost, pixels)
        self.ghosts.append(
            entityFactory.create_ghost(coordinates, pixels, red_ghost,
                                       self.can_move, Ghost.GhostColor.RED)
        )

        yellow_ghost = entityAdapter.makeYellowGhostImage()
        coordinates = (0, self.height - 1)
        pixels = self.calculate_pixels_tuple(coordinates)
        self.place_element(yellow_ghost, pixels)
        self.ghosts.append(
            entityFactory.create_ghost(coordinates, pixels, yellow_ghost,
                                       self.can_move, Ghost.GhostColor.YELLOW)
        )

        blue_ghost = entityAdapter.makeBlueGhostImage()
        coordinates = (self.width - 1, 0)
        pixels = self.calculate_pixels_tuple(coordinates)
        self.place_element(blue_ghost, pixels)
        self.ghosts.append(
            entityFactory.create_ghost(coordinates, pixels, blue_ghost,
                                       self.can_move, Ghost.GhostColor.BLUE)
        )

        pink_ghost = entityAdapter.makePinkGhostImage()
        coordinates = (self.width - 1, self.height - 1)
        pixels = self.calculate_pixels_tuple(coordinates)
        self.place_element(pink_ghost, pixels)
        self.ghosts.append(
            entityFactory.create_ghost(coordinates, pixels,
                                       pink_ghost, self.can_move,
                                       Ghost.GhostColor.PINK)
        )

    def setup_pacgums(self, entityFactory: EntityFactory) -> None:
        self.pacgums = []
        self.super_pacgums = []
        corners = Pacgum.get_corner_positions(self.width, self.height)
        center = (int((self.width - 1) / 2), int((self.height - 1) / 2))
        occupied = set(corners)
        occupied.add(center)

        def is_walkable(cell: tuple[int, int]) -> bool:
            x, y = cell
            if not (0 <= x < self.width and 0 <= y < self.height):
                return False
            return bool(self.maze.maze[y][x] != 15)

        free_cells = 0
        for x in range(self.width):
            for y in range(self.height):
                cell = (x, y)
                if is_walkable(cell) and cell not in occupied:
                    free_cells += 1
        amount = min(self.config.pacgum, free_cells)
        positions = Pacgum.get_random_positions(self.width, self.height,
                                                amount, is_walkable, occupied)

        for x, y in corners:
            self.super_pacgums.append(entityFactory.create_pacgum(x, y, True))
        for x, y in positions:
            self.pacgums.append(entityFactory.create_pacgum(x, y, False))

    def setup_entities(self) -> None:
        self.setup_player(self.entity_adapter, self.entity_factory)
        self.setup_ghosts(self.entity_adapter, self.entity_factory)
        self.setup_pacgums(self.entity_factory)

    def reset_player_position(self) -> None:
        self.player.x = int((self.width - 1) / 2)
        self.player.y = int((self.height - 1) / 2)
        px_jugador = self.calculate_pixels_tuple(
            (self.player.x, self.player.y))
        self.player.set_pixels(px_jugador)
        self.player.set_current_direction(MovingDirection.NOT_MOVING)
        self.player.desired_direction = MovingDirection.NOT_MOVING

    def draw_pacgums(self) -> None:
        color = (255, 184, 174)
        for pacgum in self.pacgums:
            pixels = self.calculate_pixels_tuple((pacgum.x, pacgum.y))
            rect = self.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 10))
            pygame.draw.circle(self.screen, color, rect.center, radius)
        for pacgum in self.super_pacgums:
            pixels = self.calculate_pixels_tuple((pacgum.x, pacgum.y))
            rect = self.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 3))
            pygame.draw.circle(self.screen, color, rect.center, radius)

    def eat_pacgums(self) -> None:
        for pacgum in list(self.pacgums):
            if pacgum.x == self.player.x and pacgum.y == self.player.y:
                self.pacgums.remove(pacgum)
                self.player.add_pacgum_points()
        for pacgum in list(self.super_pacgums):
            if pacgum.x == self.player.x and pacgum.y == self.player.y:
                self.super_pacgums.remove(pacgum)
                self.player.add_super_pacgum_points()
                self.player.power_up()
                self.power_up_timer = 0

    def lose_life_and_reset(self) -> None:
        self.player.lose_life()
        self.player.power_down()
        self.power_up_timer = 0
        if self.player.lives <= 0:
            self.running = False
            return
        self.reset_player_position()
        for ghost in self.ghosts:
            ghost.respawn()
            px_g = self.calculate_pixels_tuple((ghost.x, ghost.y))
            ghost.set_pixels(px_g)
            ghost.set_current_direction(MovingDirection.NOT_MOVING)

    def check_collisions(self) -> None:
        width_c, height_c = self.cell_size

        tolerance = 6

        p_left = self.player.x_pixel + tolerance
        p_right = self.player.x_pixel + width_c - tolerance
        p_up = self.player.y_pixel + tolerance
        p_down = self.player.y_pixel + height_c - tolerance

        for ghost in self.ghosts:
            g_left = ghost.x_pixel + tolerance
            g_right = ghost.x_pixel + width_c - tolerance
            g_up = ghost.y_pixel + tolerance
            g_down = ghost.y_pixel + height_c - tolerance

            separated = (p_right < g_left or p_left > g_right or
                         p_down < g_up or p_up > g_down)

            if not separated:
                if self.player.is_powered_up:
                    self.player.add_ghost_points()
                    ghost.respawn()
                    px_ghost = self.calculate_pixels_tuple((ghost.x, ghost.y))
                    ghost.set_pixels(px_ghost)
                    ghost.set_current_direction(MovingDirection.NOT_MOVING)
                else:
                    self.lose_life_and_reset()
                    lives = self.player.lives
                    print(f"¡Te han tocado! Vidas restantes: {lives}")
                    break

    def bind_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in self.KEY_DIRECTIONS:
                    self.player.desired_direction = self.KEY_DIRECTIONS[
                        event.key]

    def event_loop(self) -> None:
        clock = pygame.time.Clock()
        movement_interval = 35
        time_counter = 0
        self.running = True
        while self.running:
            self.print_map()
            dt = clock.tick(60)
            time_counter += dt
            if self.player.is_powered_up:
                self.power_up_timer += dt
                if self.power_up_timer >= self.POWER_UP_DURATION:
                    self.player.power_down()
                    self.power_up_timer = 0
            self.level_timer += dt
            if self.level_timer >= self.config.level_max_time * 1000:
                print("Tiempo agotado")
                self.lose_life_and_reset()
                print(f"Vidas restantes: {self.player.lives}")
                self.level_timer = 0
            self.bind_events()
            self.eat_pacgums()
            if not self.pacgums:
                self.next_level()
            if time_counter >= movement_interval:
                if self.player.current_direction == MovingDirection.NOT_MOVING:
                    self.player.update_direction()
                if self.player.current_direction != MovingDirection.NOT_MOVING:
                    self.calculate_next_movement(self.player)
                    if self.player.current_direction == (MovingDirection.
                                                         NOT_MOVING):
                        self.player.update_direction()
                player_pos = (self.player.x, self.player.y)
                for ghost in self.ghosts:
                    if ghost.current_direction != MovingDirection.NOT_MOVING:
                        self.calculate_next_movement(ghost)
                    else:
                        if self.player.is_powered_up:
                            ghost.run_from_player(player_pos)
                        else:
                            ghost.catch_player(player_pos)
                time_counter -= movement_interval
            pygame.display.flip()
        pygame.quit()
