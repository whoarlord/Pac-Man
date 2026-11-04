from src.Pygame import MazeGrid, MazeUi, EntitiesAdapter
from pygame import (Surface, draw, display, font, time,
                    Rect, transform,
                    K_UP, K_w, K_DOWN, K_s, K_ESCAPE,
                    K_p, K_RETURN, K_KP_ENTER)
from typing import Tuple
from src.Entities import (MovementEntity, Ghost, Player, MovingDirection,
                          Pacgum)


class MazeRenderer:
    def __init__(self, maze_grid: MazeGrid,
                 game_state: MazeUi, entity_adapter: EntitiesAdapter):
        self.maze_grid = maze_grid
        self.game_state = game_state
        self.entity_adapter = entity_adapter
        self.screen: Surface = display.set_mode(
            self.maze_grid.get_window_size())
        self.screen.fill("black")
        self.initialize_veil()
        self.font = font.Font(None, 40)
        self.title_font = font.Font(None, 80)
        self.pause_options = ["Resume", "Return to Main Menu"]
        self.life_anim_active = False
        self.life_anim_time = 0
        self.life_anim_image: Surface | None = None
        self.life_anim_duration = 1000
        self.RESPAWN_DELAY = 5000

    def initialize_veil(self) -> None:
        self.pause_veil = Surface(self.maze_grid.get_window_size())
        self.pause_veil.set_alpha(150)
        self.pause_veil.fill((0, 0, 0))

    def place_player_center(self, player: Surface) -> None:
        x, y = self.maze_grid.calculate_center()
        pixels = self.maze_grid.calculate_pixels_tuple((x, y))
        self.place_element(player, pixels)

    def place_entity(self, player: MovementEntity) -> None:
        pixels = player.get_pixels()
        self.place_element(player.image, pixels)

    def place_element(self, element: Surface,
                      coordinates: Tuple[int, int]) -> None:
        rect = self.maze_grid.calculate_rect_for_cell(coordinates)
        self.screen.blit(element, rect)

    def create_rect(self, init_x: float, init_y: float, finish_x: float,
                    finish_y: float, N: bool, E: bool, W: bool,
                    S: bool) -> None:
        lines_color = self.maze_grid.get_lines_color()
        thick = self.maze_grid.get_thick()
        if (N):
            draw.line(self.screen, lines_color,
                      (init_x, init_y),
                      (finish_x, init_y), thick)
        if (E):
            draw.line(self.screen, lines_color,
                      (finish_x, init_y),
                      (finish_x, finish_y), thick)
        if (W):
            draw.line(self.screen, lines_color,
                      (init_x, init_y),
                      (init_x, finish_y), thick)
        if (S):
            draw.line(self.screen, lines_color,
                      (init_x, finish_y),
                      (finish_x, finish_y), thick)

    def create_maze_block(self, cell: int, x: int, y: int,
                          x_increment: int, y_increment: int) -> None:
        N = bool(cell & 1)
        E = bool(cell & 2)
        S = bool(cell & 4)
        W = bool(cell & 8)
        self.create_rect(x, y, x + x_increment, y + y_increment, N, E, W, S)

    def make_maze(self, x_cells: int, y_cells: int) -> None:
        for i in range(y_cells):
            for j in range(x_cells):
                x0, y0 = self.maze_grid.calculate_pixels_tuple((j, i))
                x1, y1 = self.maze_grid.calculate_pixels_tuple((j + 1, i + 1))
                self.create_maze_block(self.game_state.get_maze_cell(j, i),
                                       x0, y0, x1 - x0, y1 - y0)

    def draw_hud(self) -> None:
        remaining = self.game_state.get_remaining_time()
        texts = [
            f"Score: {self.game_state.player.score}",
            f"Lives: {self.game_state.player.lives}",
            f"Level: {self.game_state.current_level + 1}",
            f"Time: {remaining}"
        ]
        for i, text in enumerate(texts):
            image = self.font.render(text, True, (255, 255, 255))
            x = 20 + i * (self.maze_grid.window_width // 4)
            y = (self.maze_grid.margin_top_height
                 + self.maze_grid.maze_height
                 + (self.maze_grid.hud_height - image.get_height()) // 2)
            self.screen.blit(image, (x, y))

    def draw_icons(self) -> None:
        current_x = 20
        margin_y = 15
        if (self.game_state.player.is_invincible()):
            img = self.entity_adapter.make_invincible_icon()
            self.screen.blit(img, (current_x, margin_y))
            current_x += img.get_width() + 20
        if (self.game_state.player.is_speed_boost()):
            img_speed = self.entity_adapter.make_speed_up_icon()
            self.screen.blit(img_speed, (current_x, margin_y))
            current_x += img_speed.get_width() + 20
        if (self.game_state.player.is_ghost_freeze()):
            img_ghost = self.entity_adapter.make_ghost_freeze_icon()
            self.screen.blit(img_ghost, (current_x, margin_y))

    def draw_map(self) -> None:
        self.screen.fill("black")
        self.make_maze(self.maze_grid.width, self.maze_grid.height)
        self.draw_pacgums()
        self.place_entity(self.game_state.player)
        for ghost in self.game_state.ghosts:
            if ghost.is_eaten():
                continue
            self.make_ghost_by_color(ghost)
            self.place_entity(ghost)
        self.draw_hud()
        self.check_collisions()
        self.draw_icons()
        dt = time.Clock().tick(60)
        self.draw_life_extra_animation(dt)

    def draw_life_extra_animation(self, dt: int) -> None:
        if not self.life_anim_active or not self.life_anim_image:
            return
        self.life_anim_time += dt
        if self.life_anim_time >= self.life_anim_duration:
            self.life_anim_active = False
            return
        progress = self.life_anim_time / self.life_anim_duration
        center_x, center_y = self.maze_grid.calculate_center_pixels()

        if progress <= 0.6:
            phase_prog = progress / 0.6
            scale_factor = 0.1 + (5.9 * phase_prog)
            orig_w, orig_h = self.life_anim_image.get_size()
            new_w = int(orig_w * scale_factor)
            new_h = int(orig_h * scale_factor)
            scaled_img = transform.scale(
                self.life_anim_image, (new_w, new_h))
            rect = scaled_img.get_rect(center=(center_x, center_y))
            self.screen.blit(scaled_img, rect.topleft)
        else:
            phase_prog = (progress - 0.6) / 0.4
            orig_w, orig_h = self.life_anim_image.get_size()
            base_w = int(orig_w * 6.0)
            base_h = int(orig_h * 6.0)
            offset = int(350 * phase_prog)
            alpha = max(0, int(255 * (1.0 - phase_prog)))
            base_img = transform.scale(self.life_anim_image,
                                       (base_w, base_h))
            w_half, h_half = base_w // 2, base_h // 2
            quads = [
                (base_img.subsurface(Rect(0, 0, w_half, h_half)),
                    -offset, -offset),         # Top-Left
                (base_img.subsurface(Rect(w_half, 0, w_half, h_half)),
                    offset, -offset),      # Top-Right
                (base_img.subsurface(Rect(0, h_half, w_half, h_half)),
                    -offset, offset),      # Bottom-Left
                (base_img.subsurface(Rect(w_half, h_half, w_half,
                                          h_half)), offset, offset)
            ]
            for quad_img, off_x, off_y in quads:
                quad_surface = quad_img.copy()
                quad_surface.set_alpha(alpha)
                q_rect = quad_surface.get_rect()
                q_rect.center = (center_x + off_x, center_y + off_y)
                self.screen.blit(quad_surface, q_rect.topleft)

    def trigger_level_skip_effect(self) -> None:
        fire_efect = Surface(self.maze_grid.get_window_size())
        fire_efect.set_alpha(120)
        fire_efect.fill((255, 140, 0))
        self.screen.blit(fire_efect, (0, 0))

        text_font = font.Font(None, 120)
        super_text = text_font.render("FIRE SALE: LEVEL SKIP", True,
                                      (255, 238, 0))
        text_rect = super_text.get_rect(
            center=self.maze_grid.calculate_center_pixels())
        self.screen.blit(super_text, text_rect.topleft)

        display.flip()
        time.wait(800)

        self.pacgums.clear()
        self.super_pacgums.clear()

    def make_ghost_by_color(self, ghost: Ghost) -> None:
        scared: bool = ghost.is_scared()
        if ghost.color == Ghost.GhostColor.RED:
            img = self.entity_adapter.makeRedGhostImage(scared)
            ghost.set_image(img)
        elif ghost.color == Ghost.GhostColor.BLUE:
            img = self.entity_adapter.makeBlueGhostImage(scared)
            ghost.set_image(img)
        elif ghost.color == Ghost.GhostColor.PINK:
            img = self.entity_adapter.makePinkGhostImage(scared)
            ghost.set_image(img)
        elif ghost.color == Ghost.GhostColor.YELLOW:
            img = self.entity_adapter.makeYellowGhostImage(scared)
            ghost.set_image(img)

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

    def setup_player(self) -> None:
        player = self.entity_adapter.makePlayerImage(
            MovingDirection.NOT_MOVING)
        coordinates: Tuple[int, int] = (int((self.maze_grid.width - 1) / 2),
                                        int((self.maze_grid.height - 1) / 2))
        pixels: Tuple[int, int] = self.maze_grid.calculate_pixels_tuple(
            coordinates)
        self.place_element(player, pixels)
        self.game_state.player = (self.game_state.entity_factory.create_player(
            coordinates, pixels, player, self.can_move,
            self.game_state.config.points_per_pacgum,
            self.game_state.config.points_per_super_pacgum,
            self.game_state.config.points_per_ghost,
            self.game_state.config.lives))

    def setup_ghosts(self) -> None:
        ghosts = []
        red_ghost = self.entity_adapter.makeRedGhostImage()
        entity_factory = self.game_state.entity_factory
        coordinates: Tuple[int, int] = (0, 0)
        pixels: Tuple[int, int] = self.maze_grid.calculate_pixels_tuple(
            coordinates)
        self.place_element(red_ghost, pixels)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels, red_ghost,
                                        self.can_move,
                                        Ghost.GhostColor.RED)
        )

        yellow_ghost = self.entity_adapter.makeYellowGhostImage()
        coordinates = (0, self.maze_grid.height - 1)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        self.place_element(yellow_ghost, pixels)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels, yellow_ghost,
                                        self.can_move,
                                        Ghost.GhostColor.YELLOW)
        )

        blue_ghost = self.entity_adapter.makeBlueGhostImage()
        coordinates = (self.maze_grid.width - 1, 0)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        self.place_element(blue_ghost, pixels)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels, blue_ghost,
                                        self.can_move,
                                        Ghost.GhostColor.BLUE)
        )

        pink_ghost = self.entity_adapter.makePinkGhostImage()
        coordinates = (self.maze_grid.width - 1, self.maze_grid.height - 1)
        pixels = self.maze_grid.calculate_pixels_tuple(coordinates)
        self.place_element(pink_ghost, pixels)
        ghosts.append(
            entity_factory.create_ghost(coordinates, pixels,
                                        pink_ghost, self.can_move,
                                        Ghost.GhostColor.PINK)
        )
        self.game_state.ghosts = ghosts

    def setup_pacgums(self) -> None:
        self.pacgums = []
        self.super_pacgums = []
        entity_factory = self.game_state.entity_factory
        width = self.maze_grid.get_width()
        height = self.maze_grid.get_height()
        corners = Pacgum.get_corner_positions(width, height)
        center = (int((width - 1) / 2), int((height - 1) / 2))
        occupied = set(corners)
        occupied.add(center)

        def is_walkable(cell: tuple[int, int]) -> bool:
            x, y = cell
            if not (0 <= x < width and 0 <= y < height):
                return False
            return bool(self.game_state.get_maze_cell(x, y) != 15)

        free_cells = 0
        for x in range(width):
            for y in range(height):
                cell = (x, y)
                if is_walkable(cell) and cell not in occupied:
                    free_cells += 1
        amount = min(self.game_state.config.pacgum, free_cells)
        positions = Pacgum.get_random_positions(width, height,
                                                amount, is_walkable, occupied)

        for x, y in corners:
            self.super_pacgums.append(entity_factory.create_pacgum(x, y, True))
        for x, y in positions:
            self.pacgums.append(entity_factory.create_pacgum(x, y, False))

    def draw_pacgums(self) -> None:
        color = (255, 184, 174)
        for pacgum in self.pacgums:
            pixels = self.maze_grid.calculate_pixels_tuple(
                (pacgum.x, pacgum.y))
            rect = self.maze_grid.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 10))
            draw.circle(self.screen, color, rect.center, radius)
        for pacgum in self.super_pacgums:
            pixels = self.maze_grid.calculate_pixels_tuple(
                (pacgum.x, pacgum.y))
            rect = self.maze_grid.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 3))
            draw.circle(self.screen, color, rect.center, radius)

    def eat_pacgums(self) -> None:
        for pacgum in list(self.pacgums):
            if (pacgum.x == self.game_state.player.x and
                    pacgum.y == self.game_state.player.y):
                self.pacgums.remove(pacgum)
                self.game_state.player.add_pacgum_points()
        for pacgum in list(self.super_pacgums):
            if (pacgum.x == self.game_state.player.x and
                    pacgum.y == self.game_state.player.y):
                self.super_pacgums.remove(pacgum)
                self.game_state.player.add_super_pacgum_points()
                self.game_state.player.power_up()
                self.game_state.scare_ghosts()
                self.game_state.power_up_timer = 0

    def reset_player_position(self) -> None:
        self.game_state.player.x = int((self.maze_grid.width - 1) / 2)
        self.game_state.player.y = int((self.maze_grid.height - 1) / 2)
        px_jugador = self.maze_grid.calculate_pixels_tuple(
            (self.game_state.player.x, self.game_state.player.y))
        self.game_state.player.set_pixels(px_jugador)
        self.game_state.player.set_current_direction(
            MovingDirection.NOT_MOVING)
        self.game_state.player.desired_direction = MovingDirection.NOT_MOVING

    def lose_life_and_reset(self) -> None:
        self.game_state.lose_life_and_reset()
        self.reset_player_position()
        for ghost in self.game_state.ghosts:
            px_g = self.maze_grid.calculate_pixels_tuple((ghost.x, ghost.y))
            ghost.set_pixels(px_g)
            ghost.set_current_direction(MovingDirection.NOT_MOVING)

    def check_collisions(self) -> None:
        if (self.game_state.player.is_invincible()):
            return
        width_c, height_c = self.maze_grid.get_cell_size()

        tolerance = min(6, int(min(width_c, height_c) / 4))

        p_left = self.game_state.player.x_pixel + tolerance
        p_right = self.game_state.player.x_pixel + width_c - tolerance
        p_up = self.game_state.player.y_pixel + tolerance
        p_down = self.game_state.player.y_pixel + height_c - tolerance

        for ghost in self.game_state.ghosts:
            if ghost.is_eaten():
                continue
            g_left = ghost.x_pixel + tolerance
            g_right = ghost.x_pixel + width_c - tolerance
            g_up = ghost.y_pixel + tolerance
            g_down = ghost.y_pixel + height_c - tolerance

            separated = (p_right < g_left or p_left > g_right or
                         p_down < g_up or p_up > g_down)

            if not separated:
                if ghost.is_scared():
                    ghost.scared = False
                    ghost.respawn_timer = self.RESPAWN_DELAY
                    self.game_state.player.add_ghost_points()
                    ghost.respawn()
                    px_ghost = self.maze_grid.calculate_pixels_tuple(
                        (ghost.x, ghost.y))
                    ghost.set_pixels(px_ghost)
                    ghost.set_current_direction(MovingDirection.NOT_MOVING)
                else:
                    self.lose_life_and_reset()
                    lives = self.game_state.player.lives
                    print(f"¡You have been touched! Remaining lives: {lives}")
                    break

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

    def initialize_level(self) -> None:
        self.entity_adapter = EntitiesAdapter(self.maze_grid.get_cell_size())
        self.game_state.player.set_image(self.entity_adapter.makePlayerImage(
            MovingDirection.NOT_MOVING))
        self.reset_player_position()
        self.setup_ghosts()
        self.setup_pacgums()

    def setup_entities(self) -> None:
        self.game_state.initializeMaze(self.maze_grid.width,
                                       self.maze_grid.height)
        self.setup_player()
        self.setup_ghosts()
        self.setup_pacgums()

    def reset(self) -> None:
        width = self.game_state.config.levels[0].width
        height = self.game_state.config.levels[0].height
        self.game_state.reset(width, height)
        self.maze_grid.reset(width, height)
        self.screen.fill("black")

    def draw_pause_menu(self) -> None:
        self.screen.blit(self.pause_veil, (0, 0))
        title = self.title_font.render("PAUSED", True, (255, 238, 0))
        x_title = (self.maze_grid.window_width - title.get_width()) // 2
        self.screen.blit(title, (x_title, 300))
        for i, option in enumerate(self.pause_options):
            if i == self.game_state.pause_index:
                color = (255, 255, 255)
            else:
                color = (100, 100, 100)
            text = self.font.render(option, True, color)
            x = (self.maze_grid.window_width - text.get_width()) // 2
            self.screen.blit(text, (x, 450 + i * 70))

    def handle_pause_key(self, key: int) -> None:
        gs = self.game_state
        if key in (K_UP, K_w):
            gs.pause_index = (gs.pause_index - 1) % len(self.pause_options)
        elif key in (K_DOWN, K_s):
            gs.pause_index = (gs.pause_index + 1) % len(self.pause_options)
        elif key in (K_ESCAPE, K_p):
            gs.paused = False
        elif key in (K_RETURN, K_KP_ENTER):
            gs.paused = False
            if gs.pause_index == 1:
                gs.back_to_menu = True
                gs.running = False

    def can_move(self, origin: tuple[int, int],
                 target: tuple[int, int]) -> bool:
        x_target, y_target = target
        if (x_target < 0 or x_target >= self.maze_grid.width or y_target < 0
                or y_target >= self.maze_grid.height):
            return False
        x_origin, y_origin = origin
        actual_cell = self.game_state.get_maze_cell(x_origin, y_origin)
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

    def extra_life_animation(self) -> None:
        self.life_anim_active = True
        self.life_anim_time = 0
        self.life_anim_image = (
            self.entity_adapter.make_extra_live_icon())

    def handle_animations(self, animations: dict[str, bool]) -> None:
        if (animations.get('extra_life')):
            self.extra_life_animation()
        if (animations.get('level_skip')):
            self.trigger_level_skip_effect()

    def event_loop(self) -> None:
        clock = time.Clock()
        movement_interval = 35
        time_counter = 0
        self.game_state.running = True
        while self.game_state.running:
            self.draw_map()
            dt = clock.tick(60)
            animations = self.game_state.bind_events(self.handle_pause_key)
            self.handle_animations(animations)
            if self.game_state.paused:
                self.draw_pause_menu()
                display.flip()
                continue
            time_counter += dt
            player = self.game_state.player
            if player.is_powered_up:
                self.game_state.power_up_timer += dt
                if (self.game_state.power_up_timer >=
                        self.game_state.POWER_UP_DURATION):
                    player.power_down()
                    for ghost in self.game_state.ghosts:
                        ghost.scared = False
                    self.game_state.power_up_timer = 0
            for ghost in self.game_state.ghosts:
                if ghost.is_eaten():
                    ghost.respawn_timer = max(0, ghost.respawn_timer - dt)
            self.game_state.level_timer += dt
            if (self.game_state.level_timer >=
                    self.game_state.config.level_max_time * 1000):
                print("Time is up")
                self.lose_life_and_reset()
                print(f"Remaining lives: {player.lives}")
                self.game_state.level_timer = 0
            self.eat_pacgums()
            if not self.pacgums and not self.super_pacgums:
                self.load_level()
            if time_counter >= movement_interval:
                if player.current_direction == MovingDirection.NOT_MOVING:
                    player.update_direction()
                if player.current_direction != MovingDirection.NOT_MOVING:
                    self.calculate_next_movement(player)
                player_pos = (player.x, player.y)
                if not player.is_ghost_freeze():
                    for ghost in self.game_state.ghosts:
                        if ghost.is_eaten():
                            continue
                        if (ghost.current_direction !=
                                MovingDirection.NOT_MOVING):
                            self.calculate_next_movement(ghost)
                        else:
                            if ghost.is_scared():
                                ghost.run_from_player(player_pos)
                            else:
                                ghost.catch_player(player_pos)
                time_counter -= movement_interval
            display.flip()
