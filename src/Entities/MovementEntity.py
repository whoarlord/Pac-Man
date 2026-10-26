from pygame import Surface
from typing import Callable, Tuple
from enum import Enum


class MovingDirection(Enum):
    NOT_MOVING = 0
    MOVING_UP = 1
    MOVING_DOWN = 2
    MOVING_LEFT = 3
    MOVING_RIGHT = 4


class MovementEntity():
    """Pac-Man entity: stores its position.

    The position is stored as (x, y), where x is the column and y
    is the row.
    The origin (0, 0) is the top-left corner, so y grows downwards.
    This class does not know the map: checking walls and collisions is
    done outside, and these methods are called when needed.
    """

    def __init__(self, x: int, y: int, x_pixel: int,
                 y_pixel: int, image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool]) -> None:
        """Create an entity at position (x, y)."""

        self.x = x
        self.x_pixel = x_pixel
        self.y = y
        self.y_pixel = y_pixel
        self.image = image
        self.can_move = can_move
        self.current_direction = MovingDirection.NOT_MOVING
        self.desired_direction = MovingDirection.NOT_MOVING
        self.rotation: int = 0
        self.try_move_mapper = {
            MovingDirection.MOVING_DOWN: self.try_move_down,
            MovingDirection.MOVING_LEFT: self.try_move_left,
            MovingDirection.MOVING_RIGHT: self.try_move_right,
            MovingDirection.MOVING_UP: self.try_move_up
        }

    def set_image(self, image: Surface) -> None:
        self.image = image

    def move_up(self) -> None:
        """Move the entity one cell up."""
        self.y = self.y - 1

    def move_down(self) -> None:
        """Move the entity one cell down."""
        self.y = self.y + 1

    def move_left(self) -> None:
        """Move the entity one cell to the left."""
        self.x = self.x - 1

    def move_right(self) -> None:
        """Move the entity one cell to the right."""
        self.x = self.x + 1

    def try_move_player(self, direction: MovingDirection) -> bool:
        if (direction != MovingDirection.NOT_MOVING):
            self.try_move_mapper[direction]()
        return self.desired_direction != MovingDirection.NOT_MOVING

    def update_direction(self) -> None:
        if self.try_move_player(self.desired_direction):
            self.current_direction = self.desired_direction
        elif not self.try_move_player(self.current_direction):
            self.current_direction = MovingDirection.NOT_MOVING

    def try_move_up(self) -> None:
        if (self.can_move((self.x, self.y), self.next_pos_up())):
            self.move_up()

    def try_move_down(self) -> None:
        if (self.can_move((self.x, self.y), self.next_pos_down())):
            self.move_down()

    def try_move_left(self) -> None:
        if (self.can_move((self.x, self.y), self.next_pos_left())):
            self.move_left()

    def try_move_right(self) -> None:
        if (self.can_move((self.x, self.y), self.next_pos_right())):
            self.move_right()

    def set_current_direction(self,
                              current_direction: MovingDirection) -> None:
        if (isinstance(current_direction, MovingDirection)):
            self.current_direction = current_direction

    def get_pixels(self) -> Tuple[int, int]:
        return (self.x_pixel, self.y_pixel)

    def set_pixels(self, pixels: Tuple[int, int]) -> None:
        if (isinstance(pixels[0], int)
                and isinstance(pixels[1], int)):
            self.x_pixel = pixels[0]
            self.y_pixel = pixels[1]

    def get_coordinates(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def next_pos_up(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving up.

        It does not move the entity. Use it to check the map before
        calling move_up.
        """

        return (self.x, self.y - 1)

    def next_pos_down(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving down.

        It does not move the entity.
        """

        return (self.x, self.y + 1)

    def next_pos_right(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving right.

        It does not move the entity.
        """

        return (self.x + 1, self.y)

    def next_pos_left(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving left.

        It does not move the entity.
        """

        return (self.x - 1, self.y)
