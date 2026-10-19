from src.movement_entity import Movement_entity


class Ghost(Movement_entity):
    """Pac-Man ghost: chases the player or runs away from it.

    Which of the two to use depends on player.is_powered_up, and that
    is checked outside this class.
    """

    def __init__(self, x, y) -> None:
        """Create a ghost at position (x, y)."""

        super().__init__(x, y)

    # Los métodos no tienen tipo de retorno ahora mismo, porque queda pendiente
    # de decidir si mover directamente o devolver la dirección.
    # Hay que añadir tambien el parámetro del mapa cuando decidamos como va a
    # llegar: Necesito saber qué casillas se pueden pisar y qué tamaño tiene
    # el mapa, para no salirme de los bordes.

    def catch_player(self, player_pos: tuple[int, int]) -> None:
        """Pick the neighbouring cell that gets the ghost closest to
        the player, whose position is player_pos as (x, y).
        """

        pass

    def run_from_player(self, player_pos: tuple[int, int]) -> None:
        """Pick the neighbouring cell that puts the ghost farthest from
        the player, whose position is player_pos as (x, y).
        """

        pass
