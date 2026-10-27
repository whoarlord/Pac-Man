from pygame import Surface
from typing import Callable
from src.Entities.MovementEntity import MovementEntity, MovingDirection


class Player(MovementEntity):
    """Pac-Man player: adds score and power-up state to MovementEntity."""

    def __init__(self, x: int, y: int,
                 x_pixel: int, y_pixel: int,
                 image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool],
                 points_per_pacgum: int, points_per_super_pacgum: int,
                 points_per_ghost: int, lives: int) -> None:
        """Create player with position (x, y), score 0 and not powered up."""
        super().__init__(x, y, x_pixel, y_pixel, image, can_move)
        self.score = 0
        self.is_powered_up = False
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.lives = lives
        self.pacman_state: int = 0
        self.invincible: bool = False

    def add_pacgum_points(self) -> None:
        """Add POINTS_PER_PACGUM to the score.

        It only updates the score: removing the pac-gum from the map
        is not done here.
        """

        self.score = self.points_per_pacgum + self.score

    def add_super_pacgum_points(self) -> None:
        """Add POINTS_PER_SUPER_PACGUM to the score.

        It does not activate the power-up state; call power_up for that.
        """

        self.score = self.points_per_super_pacgum + self.score

    def add_ghost_points(self) -> None:
        """Add POINTS_PER_GHOST to the score."""

        self.score = self.points_per_ghost + self.score

    def power_up(self) -> None:
        """Set is_powered_up to True (the player ate a super pac-gum).

        While it is True, ghosts should run away instead of chasing.
        """

        self.is_powered_up = True

    def power_down(self) -> None:
        """Set is_powered_up to False (the super pac-gum effect ended).

        Calling it when the player is already powered down changes nothing.
        """

        self.is_powered_up = False

    def lose_life(self) -> None:
        self.lives = max(0, self.lives - 1)

    def update_direction(self) -> None:
        if self.try_move_player(self.desired_direction):
            self.current_direction = self.desired_direction
        elif not self.try_move_player(self.current_direction):
            self.current_direction = MovingDirection.NOT_MOVING

    def change_invincibility(self):
        if (self.invincible):
            self.invincible = False
        else:
            self.invincible = True

    def is_invincible(self):
        return self.invincible
