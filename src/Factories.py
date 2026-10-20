from src.ghost import Ghost
from src.player import Player


class EntityFactory:
    """Factory that creates the Pac-Man entities (player and ghosts).

    It does not store anything: the starting positions are given to
    initialize_entity, and all creation goes through the _create_...
    methods.
    """

    def _create_player(self, x: int, y: int) -> Player:
        """Create a Player at position (x, y)."""

        return Player(x, y)

    def _create_ghost(self, x: int, y: int) -> Ghost:
        """Create a Ghost at position (x, y)."""

        return Ghost(x, y)

    def initialize_entity(self, player_pos: tuple[int, int],
                          ghosts_pos: list[tuple[int, int]]
                          ) -> tuple[Player, list[Ghost]]:
        """Create the player and one ghost for each given position.

        player_pos is the starting position of the player as (x, y),
        where x is the column and y is the row. ghosts_pos is a list of
        (x, y) positions, one for each ghost to create.

        Return a tuple (player, ghosts), where ghosts keeps the same
        order as ghosts_pos.
        """

        player_x, player_y = player_pos
        player = self._create_player(player_x, player_y)

        ghosts: list[Ghost] = []
        for ghost_pos in ghosts_pos:
            ghost_x, ghost_y = ghost_pos
            ghost = self._create_ghost(ghost_x, ghost_y)
            ghosts.append(ghost)

        return (player, ghosts)
