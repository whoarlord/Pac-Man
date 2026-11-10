"""Base class for the Pac-Man entities that move on the map."""

from pygame import Surface
from typing import Callable, Tuple
from enum import Enum


class MovingDirection(Enum):
    """Possible directions of movement of an entity.

    Attributes:
        NOT_MOVING: The entity is standing still.
        MOVING_UP: The entity moves up (y decreases).
        MOVING_DOWN: The entity moves down (y increases).
        MOVING_LEFT: The entity moves left (x decreases).
        MOVING_RIGHT: The entity moves right (x increases).
    """

    NOT_MOVING = 0
    MOVING_UP = 1
    MOVING_DOWN = 2
    MOVING_LEFT = 3
    MOVING_RIGHT = 4


class MovementEntity():
    """Base class for the Pac-Man entities that move on the map.

    The position is stored as (x, y), where x is the column and y
    is the row.
    The origin (0, 0) is the top-left corner, so y grows downwards.
    This class does not know the map: checking walls and collisions is
    done outside, and these methods are called when needed.

    Attributes:
        x: Column of the entity.
        y: Row of the entity.
        x_pixel: Horizontal position in pixels.
        y_pixel: Vertical position in pixels.
        image: Surface used to draw the entity.
        can_move: Function that tells whether a move is allowed.
        current_direction: Direction the entity is moving in.
        desired_direction: Direction the entity wants to take.
        rotation: Rotation applied to the image.
        try_move_mapper: Maps each direction to its try_move method.
    """

    def __init__(self, x: int, y: int, x_pixel: int,
                 y_pixel: int, image: Surface,
                 can_move: Callable[
                     [tuple[int, int], tuple[int, int]], bool]) -> None:
        """Create an entity at position (x, y), standing still.

        Args:
            x: Column of the entity.
            y: Row of the entity.
            x_pixel: Horizontal position in pixels.
            y_pixel: Vertical position in pixels.
            image: Surface used to draw the entity.
            can_move: Function that receives the current cell and the
                target cell, and returns True if the move is allowed.
        """

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
        """Change the image used to draw the entity.

        Args:
            image: New surface for the entity.
        """

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
        """Try to move one cell in the given direction.

        The move is only made if can_move allows it. NOT_MOVING does
        nothing.

        Args:
            direction: Direction to try to move in.

        Returns:
            True if desired_direction is not NOT_MOVING, False
            otherwise. Note that it does not tell whether the entity
            actually moved.
        """

        if (direction != MovingDirection.NOT_MOVING):
            self.try_move_mapper[direction]()
        return self.desired_direction != MovingDirection.NOT_MOVING

    def update_direction(self) -> None:
        """Move the entity and update current_direction.

        It first tries desired_direction. If there is none, it keeps
        moving in current_direction. If neither is possible,
        current_direction becomes NOT_MOVING.
        """

        if self.try_move_player(self.desired_direction):
            self.current_direction = self.desired_direction
        elif not self.try_move_player(self.current_direction):
            self.current_direction = MovingDirection.NOT_MOVING

    def try_move_up(self) -> None:
        """Move one cell up if can_move allows it."""

        if (self.can_move((self.x, self.y), self.next_pos_up())):
            self.move_up()

    def try_move_down(self) -> None:
        """Move one cell down if can_move allows it."""

        if (self.can_move((self.x, self.y), self.next_pos_down())):
            self.move_down()

    def try_move_left(self) -> None:
        """Move one cell to the left if can_move allows it."""

        if (self.can_move((self.x, self.y), self.next_pos_left())):
            self.move_left()

    def try_move_right(self) -> None:
        """Move one cell to the right if can_move allows it."""

        if (self.can_move((self.x, self.y), self.next_pos_right())):
            self.move_right()

    def set_current_direction(self,
                              current_direction: MovingDirection) -> None:
        """Set the current direction of the entity.

        The value is ignored if it is not a MovingDirection.

        Args:
            current_direction: New current direction.
        """

        if (isinstance(current_direction, MovingDirection)):
            self.current_direction = current_direction

    def get_pixels(self) -> Tuple[int, int]:
        """Return the position of the entity in pixels.

        Returns:
            A tuple (x_pixel, y_pixel).
        """

        return (self.x_pixel, self.y_pixel)

    def set_pixels(self, pixels: Tuple[int, int]) -> None:
        """Set the position of the entity in pixels.

        Nothing changes if any of the two values is not an integer.

        Args:
            pixels: New position as (x_pixel, y_pixel).
        """

        if (isinstance(pixels[0], int)
                and isinstance(pixels[1], int)):
            self.x_pixel = pixels[0]
            self.y_pixel = pixels[1]

    def get_coordinates(self) -> Tuple[int, int]:
        """Return the cell where the entity is.

        Returns:
            A tuple (x, y) with the column and the row.
        """

        return (self.x, self.y)

    def next_pos_up(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving up.

        It does not move the entity. Use it to check the map before
        calling move_up.

        Returns:
            The cell above the entity.
        """

        return (self.x, self.y - 1)

    def next_pos_down(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving down.

        It does not move the entity.

        Returns:
            The cell below the entity.
        """

        return (self.x, self.y + 1)

    def next_pos_right(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving right.

        It does not move the entity.

        Returns:
            The cell to the right of the entity.
        """

        return (self.x + 1, self.y)

    def next_pos_left(self) -> tuple[int, int]:
        """Return the (x, y) cell the entity would reach by moving left.

        It does not move the entity.

        Returns:
            The cell to the left of the entity.
        """

        return (self.x - 1, self.y)

    @staticmethod
    def next_pos_to_target(player_pos: tuple[int, int],
                           direction: MovingDirection,
                           number_of_movements: int) -> tuple[int, int]:
        """Return the cell reached by moving from a position.

        It does not check the map, so the result can be a wall or be
        outside the map.

        Args:
            player_pos: Starting cell as (x, y).
            direction: Direction of the movement.
            number_of_movements: Number of cells to move.

        Returns:
            The cell number_of_movements cells away from player_pos in
            the given direction. If direction is NOT_MOVING, it returns
            player_pos.
        """

        if (direction == MovingDirection.MOVING_DOWN):
            return (player_pos[0], player_pos[1] + 1 * number_of_movements)
        elif (direction == MovingDirection.MOVING_UP):
            return (player_pos[0], player_pos[1] - 1 * number_of_movements)
        elif (direction == MovingDirection.MOVING_RIGHT):
            return (player_pos[0] + 1 * number_of_movements, player_pos[1])
        elif (direction == MovingDirection.MOVING_LEFT):
            return (player_pos[0] - 1 * number_of_movements, player_pos[1])
        else:
            return (player_pos)
