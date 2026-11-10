"""Factory for the Pac-Man entities (player, ghosts and pacgums)."""

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
                      points_per_pacgum: int, points_per_super_pacgum: int,
                      points_per_ghost: int, lives: int) -> Player:
        """Create a Player at position (x, y).

        Args:
            coordinates: Starting cell of the player as (x, y).
            pixels: Starting position of the player in pixels as
                (x_pixel, y_pixel).
            image: Surface used to draw the player.
            points_per_pacgum: Points awarded for a normal pacgum.
            points_per_super_pacgum: Points awarded for a super pacgum.
            points_per_ghost: Points awarded for eating a ghost.
            lives: Number of lives the player starts with.

        Returns:
            The new Player, using the can_move function of the factory.
        """

        return Player(coordinates[0], coordinates[1],
                      pixels[0], pixels[1],
                      image, self.can_move,
                      points_per_pacgum, points_per_super_pacgum,
                      points_per_ghost, lives)

    def create_ghost(self, coordinates: Tuple[int, int],
                     pixels: Tuple[int, int], image: Surface,
                     color: Ghost.GhostColor) -> Ghost:
        """Create a Ghost at position (x, y).

        Args:
            coordinates: Starting cell of the ghost as (x, y).
            pixels: Starting position of the ghost in pixels as
                (x_pixel, y_pixel).
            image: Surface used to draw the ghost.
            color: Color of the ghost, which decides how it chases.

        Returns:
            The new Ghost, using the can_move and available_cell
            functions of the factory.
        """

        return Ghost(coordinates[0], coordinates[1],
                     pixels[0], pixels[1],
                     image, self.can_move, color,
                     self.available_cell,)

    def create_pacgum(self, x: int, y: int, is_super: bool) -> Pacgum:
        """Create a Pacgum at position (x, y).

        It is a super pacgum if is_super is True, a normal one otherwise.

        Args:
            x: Column of the pacgum.
            y: Row of the pacgum.
            is_super: True for a super pacgum, False for a normal one.

        Returns:
            The new Pacgum.
        """

        return Pacgum(x, y, is_super)

    def set_can_move(self, can_move: Callable[[tuple[int, int],
                                               tuple[int, int]], bool]
                     ) -> None:
        """Set the function used to check if an entity can move.

        Args:
            can_move: Function that receives the current cell and the
                target cell, and returns True if the move is allowed.
        """

        self.can_move = can_move

    def set_available_cell(self, available_cell: Callable[
            [tuple[int, int]], bool]) -> None:
        """Set the function used to check if a cell can be stepped on.

        Args:
            available_cell: Function that receives a cell and returns
                True if it is not a wall and is inside the map.
        """

        self.available_cell = available_cell
