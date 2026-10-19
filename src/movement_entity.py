from abc import ABC


class Movement_entity(ABC):
    def __init__(self, x: int, y: int) -> None:
        """Create a player at position (x, y) with score 0
        and not powered up.
        """

        self.x = x
        self.y = y
        self.score = 0
        self.is_powered_up = False

    def move_up(self) -> None:
        """Move the player one cell up."""

        self.y = self.y - 1

    def move_down(self) -> None:
        """Move the player one cell down."""

        self.y = self.y + 1

    def move_right(self) -> None:
        """Move the player one cell to the right."""

        self.x = self.x + 1

    def move_left(self) -> None:
        """Move the player one cell to the left."""

        self.x = self.x - 1

    def next_pos_up(self) -> tuple[int, int]:
        """Return the (x, y) cell the player would reach by moving up.

        It does not move the player. Use it to check the map before
        calling move_up.
        """

        return (self.x, self.y - 1)

    def next_pos_down(self) -> tuple[int, int]:
        """Return the (x, y) cell the player would reach by moving down.

        It does not move the player.
        """

        return (self.x, self.y + 1)

    def next_pos_right(self) -> tuple[int, int]:
        """Return the (x, y) cell the player would reach by moving right.

        It does not move the player.
        """

        return (self.x + 1, self.y)

    def next_pos_left(self) -> tuple[int, int]:
        """Return the (x, y) cell the player would reach by moving left.

        It does not move the player.
        """

        return (self.x - 1, self.y)
