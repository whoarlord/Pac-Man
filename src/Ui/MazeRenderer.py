"""Drawing of the maze, the entities, the HUD and the effects."""

from src.Ui import MazeGrid, EntitiesAdapter, MLXAdapter
from src.Game.GameState import GameState
from pygame import (Surface, display, font, time, SRCALPHA)
from typing import Tuple
from src.Entities.Ghost import Ghost
from src.Entities.MovementEntity import MovementEntity


class MazeRenderer:
    """Draws the game on the window.

    The walls are drawn once per level in maze_ui (draw_maze). In each
    frame, draw_map draws the background, the walls, the pacgums, the
    entities, the HUD and the icons.

    Attributes:
        mlxadapter: Adapter used to draw pixels and shapes.
        maze_grid: Grid used to convert cells into pixels.
        game_state: State of the game.
        entity_adapter: Adapter that gives the images of the entities.
        screen: Window surface.
        background: Black surface used as background.
        maze_ui: Surface where the walls of the level are drawn.
        pause_veil: Semi-transparent surface drawn over the game when
            it is paused.
        fire_efect: Semi-transparent orange surface of the level skip
            effect.
        font: Font of the HUD and the menus.
        title_font: Font of the title of the pause menu.
        POWER_UP_WARNING: Milliseconds before the end of the power-up in
            which the scared ghosts blink.
        BLINK_INTERVAL: Milliseconds between blinks.
    """

    def __init__(self, maze_grid: MazeGrid,
                 game_state: GameState, entity_adapter: EntitiesAdapter
                 ) -> None:
        """Create the window and the surfaces used to draw.

        Args:
            maze_grid: Grid used to convert cells into pixels.
            game_state: State of the game.
            entity_adapter: Adapter that gives the images of the
                entities.
        """

        self.mlxadapter = MLXAdapter()
        self.maze_grid = maze_grid
        self.game_state = game_state
        self.entity_adapter = entity_adapter
        self.screen: Surface = display.set_mode(
            self.maze_grid.get_window_size())
        self.background = Surface(self.maze_grid.get_window_size())
        self.maze_ui = Surface(self.maze_grid.get_window_size())
        self.mlxadapter.set_color(self.background, 'black')
        self.initialize_veil()
        self.initialize_fire_efect()
        self.font = font.Font(None, 40)
        self.title_font = font.Font(None, 80)
        self.POWER_UP_WARNING = 2000
        self.BLINK_INTERVAL = 200

    def initialize_veil(self) -> None:
        """Create the semi-transparent black surface of the pause."""

        self.pause_veil = Surface(self.maze_grid.get_window_size(), SRCALPHA)
        self.mlxadapter.set_color(self.pause_veil, 'black')
        self.mlxadapter.set_alpha(self.pause_veil, 150)

    def initialize_fire_efect(self) -> None:
        """Create the semi-transparent orange surface of the level skip."""

        self.fire_efect = Surface(self.maze_grid.get_window_size(), SRCALPHA)
        self.mlxadapter.set_color(self.fire_efect, 'orange')
        self.mlxadapter.set_alpha(self.fire_efect, 120)

    def place_entity(self, player: MovementEntity) -> None:
        """Draw an entity at its pixel position.

        Args:
            player: Entity to draw (any MovementEntity).
        """

        pixels = player.get_pixels()
        self.place_element(player.image, pixels)

    def place_element(self, element: Surface,
                      coordinates: Tuple[int, int]) -> None:
        """Draw a surface at a position in pixels.

        Args:
            element: Surface to draw.
            coordinates: Top-left corner as (x, y) in pixels.
        """

        rect = self.maze_grid.calculate_rect_for_cell(coordinates)
        self.screen.blit(element, rect)

    def create_rect(self, init_x: int, init_y: int, finish_x: int,
                    finish_y: int, N: bool, E: bool, W: bool,
                    S: bool) -> None:
        """Draw the walls of a rectangle in maze_ui.

        Each side is drawn only if its flag is True.

        Args:
            init_x: Pixel column of the left side.
            init_y: Pixel row of the top side.
            finish_x: Pixel column of the right side.
            finish_y: Pixel row of the bottom side.
            N: True to draw the top side.
            E: True to draw the right side.
            W: True to draw the left side.
            S: True to draw the bottom side.
        """

        lines_color = self.maze_grid.get_lines_color()
        thick = self.maze_grid.get_thick()
        if (N):
            self.mlxadapter.draw_line(self.maze_ui, lines_color,
                                      (init_x, init_y),
                                      (finish_x, init_y), thick)
        if (E):
            self.mlxadapter.draw_line(self.maze_ui, lines_color,
                                      (finish_x, init_y),
                                      (finish_x, finish_y), thick)
        if (W):
            self.mlxadapter.draw_line(self.maze_ui, lines_color,
                                      (init_x, init_y),
                                      (init_x, finish_y), thick)
        if (S):
            self.mlxadapter.draw_line(self.maze_ui, lines_color,
                                      (init_x, finish_y),
                                      (finish_x, finish_y), thick)

    def create_maze_block(self, cell: int, x: int, y: int,
                          x_increment: int, y_increment: int) -> None:
        """Draw the walls of one cell in maze_ui.

        Args:
            cell: Value of the cell in the maze. Its bits say which
                walls it has: 1 top, 2 right, 4 bottom and 8 left.
            x: Pixel column of the left side of the cell.
            y: Pixel row of the top side of the cell.
            x_increment: Width of the cell in pixels.
            y_increment: Height of the cell in pixels.
        """

        N = bool(cell & 1)
        E = bool(cell & 2)
        S = bool(cell & 4)
        W = bool(cell & 8)
        self.create_rect(x, y, x + x_increment, y + y_increment, N, E, W, S)

    def make_maze(self, x_cells: int, y_cells: int) -> None:
        """Draw the walls of the whole maze in maze_ui.

        Args:
            x_cells: Number of columns of the maze.
            y_cells: Number of rows of the maze.
        """

        for i in range(y_cells):
            for j in range(x_cells):
                x0, y0 = self.maze_grid.calculate_pixels_tuple((j, i))
                x1, y1 = self.maze_grid.calculate_pixels_tuple((j + 1, i + 1))
                self.create_maze_block(self.game_state.get_maze_cell(j, i),
                                       x0, y0, x1 - x0, y1 - y0)

    def draw_hud(self) -> None:
        """Draw the HUD: score, lives, level (from 1) and remaining time.

        The four texts are drawn in columns in the area below the maze.
        """

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
        """Draw the icons of the active cheats.

        The icons of the invincibility, the speed boost and the ghost
        freeze are drawn in this order, from left to right, above the
        maze.
        """

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
        """Draw a frame of the game.

        It draws the background, the walls, the pacgums, the player, the
        ghosts that are not eaten, the HUD and the icons. It does not
        update the display.
        """

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.maze_ui, (0, 0))
        self.draw_pacgums()
        self.place_entity(self.game_state.player)
        for ghost in self.game_state.ghosts:
            if ghost.is_eaten():
                continue
            self.make_ghost_by_color(ghost)
            self.place_entity(ghost)
        self.draw_hud()
        self.draw_icons()

    def draw_maze(self) -> None:
        """Draw the walls of the current level again.

        The walls are drawn in maze_ui and then on the screen. Call it
        when a level is loaded.
        """

        self.maze_ui.blit(self.background, (0, 0))
        self.make_maze(self.maze_grid.width, self.maze_grid.height)
        self.screen.blit(self.maze_ui, (0, 0))

    def trigger_level_skip_effect(self) -> None:
        """Show the level skip effect.

        It draws the orange veil and the text 'FIRE SALE: LEVEL SKIP' in
        the center, updates the display and waits 800 milliseconds, so
        the game stops during that time.
        """

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
        """Set the image of a ghost according to its color and state.

        A scared ghost uses the scared image. In the last
        POWER_UP_WARNING milliseconds of the power-up, it alternates
        between the scared and the normal image every BLINK_INTERVAL
        milliseconds.

        Args:
            ghost: Ghost whose image is set.
        """

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
        """Draw the pacgums as circles.

        The radius of a normal pacgum is a tenth of the cell (at least
        1 pixel) and the one of a super pacgum is a third.
        """

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
        """Draw the pause menu over the game.

        It draws the veil, the title and the options. The selected
        option is white and the others are gray.
        """

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
        """Show the extra life animation.

        It draws the icon of the extra life, three times the size of a
        cell, in the center of the window for 250 milliseconds, so the
        game stops during that time.
        """

        original_icon = self.entity_adapter.make_extra_live_icon()
        cell_w, cell_h = self.maze_grid.get_cell_size()
        proportional_size = (cell_w * 3, cell_h * 3)
        big_icon = self.mlxadapter.scale_image(original_icon,
                                               proportional_size)
        center_x, center_y = self.maze_grid.calculate_center_pixels()
        icon_rect = big_icon.get_rect(center=(center_x, center_y))
        self.draw_map()
        self.screen.blit(big_icon, icon_rect.topleft)
        display.flip()
        time.wait(250)
