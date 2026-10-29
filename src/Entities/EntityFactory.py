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
