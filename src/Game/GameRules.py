"""Rules of the Pac-Man game: eating, collisions and timers."""

from src.Game.GameState import GameState
from src.Ui.MazeGrid import MazeGrid
from src.Game.LevelLoader import LevelLoader
from src.Entities.MovementEntity import MovingDirection


class GameRules:
    """Applies the rules of the game on the game state.

    Attributes:
        game_state: State of the game.
        maze_grid: Grid used to convert cells into pixels.
        level_loader: Loader used to put the player back in the center.
    """

    def __init__(self, game_state: GameState, maze_grid: MazeGrid,
                 level_loader: LevelLoader) -> None:
        """Create the rules.

        Args:
            game_state: State of the game.
            maze_grid: Grid used to convert cells into pixels.
            level_loader: Loader used to put the player back in the
                center.
        """

        self.game_state = game_state
        self.maze_grid = maze_grid
        self.level_loader = level_loader

    def eat_pacgums(self) -> None:
        """Eat the pacgums that are in the cell of the player.

        A normal pacgum is removed and adds points_per_pacgum to the
        score. A super pacgum is removed, adds points_per_super_pacgum,
        powers up the player, scares the ghosts and resets
        power_up_timer.
        """

        for pacgum in list(self.game_state.pacgums):
            if (pacgum.x == self.game_state.player.x and
                    pacgum.y == self.game_state.player.y):
                self.game_state.pacgums.remove(pacgum)
                self.game_state.player.add_pacgum_points()
        for pacgum in list(self.game_state.super_pacgums):
            if (pacgum.x == self.game_state.player.x and
                    pacgum.y == self.game_state.player.y):
                self.game_state.super_pacgums.remove(pacgum)
                self.game_state.player.add_super_pacgum_points()
                self.game_state.player.power_up()
                self.game_state.scare_ghosts()
                self.game_state.power_up_timer = 0

    def lose_life_and_reset(self) -> None:
        """Take a life from the player and send the entities back.

        It calls GameState.lose_life_and_reset, puts the player back in
        the center of the maze and, for each ghost, updates its pixel
        position to its respawn cell and stops it.
        """

        self.game_state.lose_life_and_reset()
        self.level_loader.reset_player_position()
        for ghost in self.game_state.ghosts:
            px_g = self.maze_grid.calculate_pixels_tuple((ghost.x, ghost.y))
            ghost.set_pixels(px_g)
            ghost.set_current_direction(MovingDirection.NOT_MOVING)

    def check_collisions(self) -> None:
        """Check the collisions between the player and the ghosts.

        The collision is checked with the pixel positions. Each entity
        is a square of the size of a cell, reduced on every side by a
        tolerance of min(6, cell_size / 4) pixels. Eaten ghosts are
        ignored.

        If the player touches a scared ghost, the ghost stops being
        scared, waits RESPAWN_DELAY milliseconds, goes back to its spawn
        cell and stops, and the player gets points_per_ghost. If the
        ghost is not scared and the player is not invincible, it calls
        lose_life_and_reset, prints the remaining lives and the rest of
        the ghosts are not checked in that call.
        """

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
                    ghost.respawn_timer = self.game_state.RESPAWN_DELAY
                    self.game_state.player.add_ghost_points()
                    ghost.respawn()
                    px_ghost = self.maze_grid.calculate_pixels_tuple(
                        (ghost.x, ghost.y))
                    ghost.set_pixels(px_ghost)
                    ghost.set_current_direction(MovingDirection.NOT_MOVING)
                elif not self.game_state.player.is_invincible():
                    self.lose_life_and_reset()
                    lives = self.game_state.player.lives
                    print(f"You have been touched! Remaining lives: {lives}")
                    break

    def update_timers(self, dt: int) -> None:
        """Update the timers of the game.

        While the player is powered up, power_up_timer grows. When it
        reaches POWER_UP_DURATION, the player powers down, the ghosts
        stop being scared and the timer is reset. The respawn_timer of
        the eaten ghosts goes down to 0. level_timer grows, and when it
        reaches level_max_time seconds, it prints a message, sets the
        lives of the player to 0, stops the game and resets
        level_timer.

        Args:
            dt: Milliseconds since the last frame.
        """

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
            print("Time is up! Game Over.")
            player.lives = 0
            self.game_state.running = False
            self.game_state.level_timer = 0
