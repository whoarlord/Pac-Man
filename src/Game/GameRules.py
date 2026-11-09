from src.Pygame.MazeUi import MazeUi
from src.Pygame.MazeGrid import MazeGrid
from src.Game.LevelLoader import LevelLoader
from src.Entities.MovementEntity import MovingDirection


class GameRules:
    def __init__(self, game_state: MazeUi, maze_grid: MazeGrid,
                 level_loader: LevelLoader) -> None:
        self.game_state = game_state
        self.maze_grid = maze_grid
        self.level_loader = level_loader

    def eat_pacgums(self) -> None:
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
        self.game_state.lose_life_and_reset()
        self.level_loader.reset_player_position()
        for ghost in self.game_state.ghosts:
            px_g = self.maze_grid.calculate_pixels_tuple((ghost.x, ghost.y))
            ghost.set_pixels(px_g)
            ghost.set_current_direction(MovingDirection.NOT_MOVING)

    def check_collisions(self) -> None:
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
                    print(f"¡You have been touched! Remaining lives: {lives}")
                    break

    def update_timers(self, dt: int) -> None:
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
