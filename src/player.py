class Player:
    """Pac-Man player: stores its position, score and power-up state.

    The position is stored as (x, y), where x is the column and y is the row.
    The origin (0, 0) is the top-left corner, so y grows downwards.
    This class does not know the map: checking walls and collisions is
    done outside, and these methods are called when needed.
    """

    POINTS_PER_PACGUM = 10
    POINTS_PER_SUPER_PACGUM = 50
    POINTS_PER_GHOST = 200

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

    def add_pacgum_points(self) -> None:
        """Add POINTS_PER_PACGUM to the score.

        It only updates the score: removing the pac-gum from the map
        is not done here.
        """

        self.score = self.POINTS_PER_PACGUM + self.score

    def add_super_pacgum_points(self) -> None:
        """Add POINTS_PER_SUPER_PACGUM to the score.

        It does not activate the power-up state; call power_up for that.
        """

        self.score = self.POINTS_PER_SUPER_PACGUM + self.score

    def add_ghost_points(self) -> None:
        """Add POINTS_PER_GHOST to the score."""

        self.score = self.POINTS_PER_GHOST + self.score

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


if __name__ == "__main__":
    player = Player(5, 4)
    print(f"coordinate x: {player.x}, coordinate y: {player.y}")
    test = player.next_pos_up()
    print(f"test = {test}")
    print(f"coordinate x: {player.x}, coordinate y: {player.y}")
    player.move_up()
    print(f"coordinate x: {player.x}, coordinate y: {player.y}")
    print("-----------------------------------------")
    print(f"initial score: {player.score}")
    player.add_pacgum_points()
    print(f"player after eating pacgum: {player.score}")
    player.add_super_pacgum_points()
    print(f"player after eating super_pacgum: {player.score}")
    player.add_ghost_points()
    print(f"player after eating ghost: {player.score}")
    print("-----------------------------------------")
    print(f"is the player powerd up? : {player.is_powered_up}")
    player.power_up()
    print(f"is the player powerd up? : {player.is_powered_up}")
    player.power_down()
    print(f"is the player powerd up? : {player.is_powered_up}")
