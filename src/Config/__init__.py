"""Config package: JSON loading and validation of the game settings.

Exposes the configuration parser and the Pydantic models that describe
the game and level settings.
"""

from .ConfigParser import ConfigParser, GameConfigModel, LevelConfig

__all__ = ['ConfigParser', 'GameConfigModel', 'LevelConfig']
