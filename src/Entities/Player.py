"""Player entity of the Pac-Man game."""

from pygame import Surface
from typing import Callable
from src.Entities.MovementEntity import MovementEntity, MovingDirection


class Player(MovementEntity):
    """Pac-Man player: adds score and power-up state to MovementEntity.

    Attributes:
        score: Current score of the player.
        is_powered_up: True while the super pac-gum effect is active.
        points_per_pacgum: Points awarded for a normal pac-gum.
        points_per_super_pacgum: Points awarded for a super pac-gum.
        points_per_ghost: Points awarded for eating a ghost.
        lives: Number of lives left.
        pacman_state: State used to choose the player animation frame.
        invincible: True if the player cannot be hurt by ghosts.
        speed_boost: True if the speed boost is active.
        ghost_freeze: True if the ghosts are frozen.
    """

    def __init__(self, x: int, y: int,
                 x_pixel: int, y_pixel: int,
                 image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool],
                 points_per_pacgum: int, points_per_super_pacgum: int,
                 points_per_ghost: int, lives: int) -> None:
        """Create player with position (x, y), score 0 and not powered up.

        Args:
            x: Starting column of the player.
            y: Starting row of the player.
            x_pixel: Starting horizontal position in pixels.
            y_pixel: Starting vertical position in pixels.
            image: Surface used to draw the player.
            can_move: Function that receives the current cell and the
                target cell, and returns True if the move is allowed.
            points_per_pacgum: Points awarded for a normal pac-gum.
            points_per_super_pacgum: Points awarded for a super
                pac-gum.
            points_per_ghost: Points awarded for eating a ghost.
            lives: Number of lives the player starts with.
        """

        super().__init__(x, y, x_pixel, y_pixel, image, can_move)
        self.score = 0
        self.is_powered_up = False
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.lives = lives
        self.pacman_state: int = 0
        self.invincible: bool = False
        self.speed_boost = False
        self.ghost_freeze = False

    def add_pacgum_points(self) -> None:
        """Add points_per_pacgum to the score.

        It only updates the score: removing the pac-gum from the map
        is not done here.
        """

        self.score = self.points_per_pacgum + self.score

    def add_super_pacgum_points(self) -> None:
        """Add points_per_super_pacgum to the score.

        It does not activate the power-up state; call power_up for that.
        """

        self.score = self.points_per_super_pacgum + self.score

    def add_ghost_points(self) -> None:
        """Add points_per_ghost to the score."""

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
        """Remove one life from the player, never going below 0."""

        self.lives = max(0, self.lives - 1)

    def update_direction(self) -> None:
        """Move the player and update current_direction.

        It first tries desired_direction. If there is none, it keeps
        moving in current_direction. If neither is possible,
        current_direction becomes NOT_MOVING.
        """

        if self.try_move_player(self.desired_direction):
            self.current_direction = self.desired_direction
        elif not self.try_move_player(self.current_direction):
            self.current_direction = MovingDirection.NOT_MOVING

    def change_invincibility(self) -> None:
        """Toggle the invincible state of the player."""

        if (self.invincible):
            self.invincible = False
        else:
            self.invincible = True

    def is_invincible(self) -> bool:
        """Tell whether the player is invincible.

        Returns:
            True if the player is invincible, False otherwise.
        """

        return self.invincible

    def add_extra_life(self) -> None:
        """Add one life to the player, up to a maximum of 10."""

        self.lives = min(10, self.lives + 1)

    def change_speed_boost(self) -> None:
        """Toggle the speed boost of the player."""

        if (self.speed_boost):
            self.speed_boost = False
        else:
            self.speed_boost = True

    def is_speed_boost(self) -> bool:
        """Tell whether the speed boost is active.

        Returns:
            True if the speed boost is active, False otherwise.
        """

        return self.speed_boost

    def change_ghost_freeze(self) -> None:
        """Toggle the ghost freeze effect."""

        if (self.ghost_freeze):
            self.ghost_freeze = False
        else:
            self.ghost_freeze = True

    def is_ghost_freeze(self) -> bool:
        """Tell whether the ghosts are frozen.

        Returns:
            True if the ghost freeze is active, False otherwise.
        """

        return self.ghost_freeze
