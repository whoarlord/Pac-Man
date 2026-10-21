from src.Entities.Ghost import Ghost
from src.Entities.Player import Player
from src.Entities.Pacgums import Pacgum
from pygame import Surface


class EntityFactory:
    """Factory that creates the Pac-Man entities (player, ghosts and
    pacgums).

    It does not store anything: the starting positions are given to
    initialize_entity, and all creation goes through the _create_...
    methods.
    """

    def create_player(self, x: int, y: int, image: Surface) -> Player:
        """Create a Player at position (x, y)."""

        return Player(x, y, image)

    def create_ghost(self, x: int, y: int, image: Surface,
                     color: Ghost.GhostColor) -> Ghost:
        """Create a Ghost at position (x, y)."""

        return Ghost(x, y, image, color)

    def _create_pacgum(self, x: int, y: int, is_super: bool) -> Pacgum:
        """Create a Pacgum at position (x, y).

        It is a super pacgum if is_super is True, a normal one otherwise.
        """

        return Pacgum(x, y, is_super)

    def initialize_entity(self, player_pos: tuple[int, int],
                          ghosts_pos: list[tuple[int, int]],
                          pacgums_pos: list[tuple[int, int]],
                          super_pacgums_pos: list[tuple[int, int]]
                          ) -> tuple[Player, list[Ghost],
                                     list[Pacgum], list[Pacgum]]:
        """Create the player, the ghosts and the pacgums.

        player_pos is the starting position of the player as (x, y),
        where x is the column and y is the row. ghosts_pos, pacgums_pos
        and super_pacgums_pos are lists of (x, y) positions: one ghost,
        one normal pacgum or one super pacgum is created for each one.

        Return a tuple (player, ghosts, pacgums, super_pacgums). Each
        list keeps the same order as the positions it was created from.
        """

        """ player_x, player_y = player_pos
        player = self.create_player(player_x, player_y)

        ghosts: list[Ghost] = []
        ghost_colors = [
            Ghost.GhostColor.RED,
            Ghost.GhostColor.BLUE,
            Ghost.GhostColor.PINK,
            Ghost.GhostColor.YELLOW
        ]
        for ghost_pos in ghosts_pos:
            if (len(ghost_colors) <= 0):
                break
            ghost_x, ghost_y = ghost_pos
            ghost = self.create_ghost(ghost_x, ghost_y, ghost_colors.pop())
            ghosts.append(ghost) """

        pacgums: list[Pacgum] = []
        for pacgum_pos in pacgums_pos:
            pacgum_x, pacgum_y = pacgum_pos
            pacgum = self._create_pacgum(pacgum_x, pacgum_y, False)
            pacgums.append(pacgum)

        s_pacgums: list[Pacgum] = []
        for s_pacgum_pos in super_pacgums_pos:
            s_pacgum_x, s_pacgum_y = s_pacgum_pos
            s_pacgum = self._create_pacgum(s_pacgum_x, s_pacgum_y, True)
            s_pacgums.append(s_pacgum)

        return (player, ghosts, pacgums, s_pacgums)


if __name__ == "__main__":
    factory = EntityFactory()
    player, ghosts, pacgums, s_pacgums = factory.initialize_entity(
        (2, 2),
        [(1, 1), (3, 1)],
        [(1, 0), (3, 0)],
        [(0, 0)],
    )

    # The player is created at the given position.
    result = (player.x, player.y)
    status = "OK" if result == (2, 2) else "FAIL"
    print(f"{status} player position={result} expected=(2, 2)")

    # Ghosts keep the order of ghosts_pos.
    result = []
    for ghost in ghosts:
        result.append((ghost.x, ghost.y))
    expected = [(1, 1), (3, 1)]
    status = "OK" if result == expected else "FAIL"
    print(f"{status} ghosts={result} expected={expected}")

    # Normal pacgums as (x, y, is_super): is_super must be False.
    result = []
    for pacgum in pacgums:
        result.append((pacgum.x, pacgum.y, pacgum.is_super))
    expected = [(1, 0, False), (3, 0, False)]
    status = "OK" if result == expected else "FAIL"
    print(f"{status} pacgums={result} expected={expected}")

    # Super pacgums as (x, y, is_super): is_super must be True.
    result = []
    for s_pacgum in s_pacgums:
        result.append((s_pacgum.x, s_pacgum.y, s_pacgum.is_super))
    expected = [(0, 0, True)]
    status = "OK" if result == expected else "FAIL"
    print(f"{status} super pacgums={result} expected={expected}")

    # Every object is of the right class.
    all_ok = isinstance(player, Player)
    for ghost in ghosts:
        if not isinstance(ghost, Ghost):
            all_ok = False
    for pacgum in pacgums:
        if not isinstance(pacgum, Pacgum):
            all_ok = False
    for s_pacgum in s_pacgums:
        if not isinstance(s_pacgum, Pacgum):
            all_ok = False
    status = "OK" if all_ok else "FAIL"
    print(f"{status} every object has the right class")

    # Empty lists: no ghosts and no pacgums of either kind.
    player, ghosts, pacgums, s_pacgums = factory.initialize_entity(
        (0, 0), [], [], [])
    all_ok = ghosts == [] and pacgums == [] and s_pacgums == []
    status = "OK" if all_ok else "FAIL"
    print(f"{status} empty lists: ghosts={ghosts} pacgums={pacgums} "
          f"super={s_pacgums}")
