from src.Ui import MazeGrid, EntitiesAdapter, MLXAdapter
from src.Game import GameState
from pygame import (Surface, draw, display, font, time)
from typing import Tuple
from src.Entities import (MovementEntity, Ghost)


class MazeRenderer:
    def __init__(self, maze_grid: MazeGrid,
                 game_state: GameState, entity_adapter: EntitiesAdapter):
        self.mlxadapter = MLXAdapter()
        self.maze_grid = maze_grid
        self.game_state = game_state
        self.entity_adapter = entity_adapter
        self.screen: Surface = display.set_mode(
            self.maze_grid.get_window_size())
        self.background = Surface(self.maze_grid.get_window_size())
        self.mlxadapter.set_color(self.background, 'black')
        self.initialize_veil()
        self.initialize_fire_efect()
        self.font = font.Font(None, 40)
        self.title_font = font.Font(None, 80)
        self.POWER_UP_WARNING = 2000
        self.BLINK_INTERVAL = 200

    def initialize_veil(self) -> None:
        self.pause_veil = Surface(self.maze_grid.get_window_size())
        self.mlxadapter.set_color(self.pause_veil, 'black')
        self.mlxadapter.set_alpha(self.pause_veil, 150)

    def initialize_fire_efect(self) -> None:
        self.fire_efect = Surface(self.maze_grid.get_window_size())
        self.mlxadapter.set_color(self.fire_efect, 'orange')
        self.mlxadapter.set_alpha(self.fire_efect, 120)

    """ def place_player_center(self, player: Surface) -> None:
        x, y = self.maze_grid.calculate_center()
        pixels = self.maze_grid.calculate_pixels_tuple((x, y))
        self.place_element(player, pixels) """

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

    def draw_map(self, dt: int) -> None:
        self.screen.blit(self.background, (0, 0))
        self.make_maze(self.maze_grid.width, self.maze_grid.height)
        self.draw_pacgums()
        self.place_entity(self.game_state.player)
        for ghost in self.game_state.ghosts:
            if ghost.is_eaten():
                continue
            self.make_ghost_by_color(ghost)
            self.place_entity(ghost)
        self.draw_hud()
        self.draw_icons()

    def trigger_level_skip_effect(self) -> None:
        self.screen.blit(self.fire_efect, (0, 0))

        text_font = font.Font(None, 120)
        super_text = text_font.render("FIRE SALE: LEVEL SKIP", True,
                                      (255, 238, 0))
        text_rect = super_text.get_rect(
            center=self.maze_grid.calculate_center_pixels())
        self.screen.blit(super_text, text_rect.topleft)

        display.flip()
        time.wait(800)

    def make_ghost_by_color(self, ghost: Ghost) -> None:
        scared: bool = ghost.is_scared()
        remaining = (self.game_state.POWER_UP_DURATION
                     - self.game_state.power_up_timer)
        if (scared and remaining <= self.POWER_UP_WARNING
                and (self.game_state.power_up_timer
                     // self.BLINK_INTERVAL) % 2 == 1):
            scared = False
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

    def draw_pacgums(self) -> None:
        color = (255, 184, 174)
        for pacgum in self.game_state.pacgums:
            pixels = self.maze_grid.calculate_pixels_tuple(
                (pacgum.x, pacgum.y))
            rect = self.maze_grid.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 10))
            self.mlxadapter.draw_circle(self.screen, color, rect.center,
                                        radius)
        for pacgum in self.game_state.super_pacgums:
            pixels = self.maze_grid.calculate_pixels_tuple(
                (pacgum.x, pacgum.y))
            rect = self.maze_grid.calculate_rect_for_cell(pixels)
            radius = max(1, int(min(rect.width, rect.height) / 3))
            self.mlxadapter.draw_circle(self.screen, color, rect.center,
                                        radius)

    def draw_pause_menu(self) -> None:
        self.screen.blit(self.pause_veil, (0, 0))
        title = self.title_font.render("PAUSED", True, (255, 238, 0))
        x_title = (self.maze_grid.window_width - title.get_width()) // 2
        self.screen.blit(title, (x_title, 300))
        for i, option in enumerate(self.game_state.pause_options):
            if i == self.game_state.pause_index:
                color = (255, 255, 255)
            else:
                color = (100, 100, 100)
            text = self.font.render(option, True, color)
            x = (self.maze_grid.window_width - text.get_width()) // 2
            self.screen.blit(text, (x, 450 + i * 70))

    def extra_life_animation(self) -> None:
        original_icon = self.entity_adapter.make_extra_live_icon()
        cell_w, cell_h = self.maze_grid.get_cell_size()
        proportional_size = (cell_w * 3, cell_h * 3)
        big_icon = self.mlxadapter.scale_image(original_icon,
                                               proportional_size)
        center_x, center_y = self.maze_grid.calculate_center_pixels()
        icon_rect = big_icon.get_rect(center=(center_x, center_y))
        self.draw_map(0)
        self.screen.blit(big_icon, icon_rect.topleft)
        display.flip()
        time.wait(250)
