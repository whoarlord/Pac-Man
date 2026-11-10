"""Pac-Man project root package.

Groups the entities, game logic and user interface subpackages, and
re-exports the most commonly used classes for convenience.
"""

from .Entities import (EntityFactory, Ghost, Player, MovementEntity,
                       MovingDirection)
from .Ui import EntitiesAdapter
from .Game import GameState

__all__ = ['EntityFactory', 'Ghost', 'Player',
           'MovementEntity', 'GameState', 'EntitiesAdapter', 'MovingDirection']
