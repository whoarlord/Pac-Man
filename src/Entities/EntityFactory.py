from src.Entities.Ghost import Ghost
from src.Entities.Player import Player
from src.Entities.Pacgums import Pacgum
from pygame import Surface
from typing import Callable, Tuple


class EntityFactory:
    """Factory that creates the Pac-Man entities (player, ghosts and
    pacgums).

    It does not store anything: the starting positions are given to
    initialize_entity, and all creation goes through the _create_...
    methods.
    """

    def create_player(self, coordinates: Tuple[int, int],
                      pixels: Tuple[int, int], image: Surface,
                      can_move: Callable[[tuple[int, int],
                                          tuple[int, int]], bool],
                      points_per_pacgum: int, points_per_super_pacgum: int,
                      points_per_ghost: int, lives: int) -> Player:
        """Create a Player at position (x, y)."""

        return Player(coordinates[0], coordinates[1],
                      pixels[0], pixels[1],
                      image, can_move, points_per_pacgum,
                      points_per_super_pacgum, points_per_ghost,
                      lives)

    def create_ghost(self, coordinates: Tuple[int, int],
                     pixels: Tuple[int, int], image: Surface,
                     can_move: Callable[
                         [tuple[int, int], tuple[int, int]], bool],
                     color: Ghost.GhostColor) -> Ghost:
        """Create a Ghost at position (x, y)."""

        return Ghost(coordinates[0], coordinates[1],
                     pixels[0], pixels[1],
                     image, can_move, color)

    def create_pacgum(self, x: int, y: int, is_super: bool) -> Pacgum:
        """Create a Pacgum at position (x, y).

        It is a super pacgum if is_super is True, a normal one otherwise.
        """

        return Pacgum(x, y, is_super)

    def initialize_entity(self, player_pos: tuple[int, int],
                          ghosts_pos: list[tuple[int, int]],
                          pacgums_pos: list[tuple[int, int]],
                          super_pacgums_pos: list[tuple[int, int]]
                          ) -> tuple[list[Pacgum], list[Pacgum]]:
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
            pacgum = self.create_pacgum(pacgum_x, pacgum_y, False)
            pacgums.append(pacgum)

        s_pacgums: list[Pacgum] = []
        for s_pacgum_pos in super_pacgums_pos:
            s_pacgum_x, s_pacgum_y = s_pacgum_pos
            s_pacgum = self.create_pacgum(s_pacgum_x, s_pacgum_y, True)
            s_pacgums.append(s_pacgum)

        return (pacgums, s_pacgums)
