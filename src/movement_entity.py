class MovementEntity:
    """Pac-Man entity: stores its position.

    The position is stored as (x, y), where x is the column and y
    is the row.
    The origin (0, 0) is the top-left corner, so y grows downwards.
    This class does not know the map: checking walls and collisions is
    done outside, and these methods are called when needed.
    """

    def __init__(self, x: int, y: int) -> None:
        """Create an entity at position (x, y)."""

        self.x = x
        self.y = y

    def move_up(self) -> None:
        """Move the entity one cell up."""

        self.y = self.y - 1

    def move_down(self) -> None:
        """Move the entity one cell down."""

        self.y = self.y + 1

    def move_right(self) -> None:
        """Move the entity one cell to the right."""

        self.x = self.x + 1

    def move_left(self) -> None:
        """Move the entity one cell to the left."""

        self.x = self.x - 1

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
