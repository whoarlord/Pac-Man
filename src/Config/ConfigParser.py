"""Configuration parsing for the Pac-Man game.

This module defines the Pydantic models that describe the game
configuration and a parser that loads them from a JSON file, tolerating
comments, unknown keys and invalid values.
"""

import os
import json
from typing import Any, ClassVar
from pydantic import BaseModel, Field, ValidationError, field_validator


class LevelConfig(BaseModel):
    """Configuration model for the dimensions of a single game level.

    Out-of-range values are clamped and values of the wrong type are
    replaced by the default, each with a warning printed to stdout.

    Attributes:
        width: Level width in cells. Must be between 5 and 100.
        height: Level height in cells. Must be between 5 and 100.
    """

    width: int = Field(default=20, ge=5, le=100)
    height: int = Field(default=20, ge=5, le=100)

    @field_validator("width", "height", mode="before")
    @classmethod
    def validate_dimensions(cls, v: Any, info: Any) -> int:
        """Validate a level dimension, clamping or defaulting if needed.

        Runs before Pydantic's own validation. Values below 5 are
        clamped to 5, values above 100 are clamped to 100, and values
        that cannot be converted to an integer fall back to 20.

        Args:
            v: Raw value read from the configuration.
            info: Pydantic validation info, used to get the field name
                for the warning messages.

        Returns:
            A valid integer dimension between 5 and 100.
        """

        field_name = (info.field_name if hasattr(info, 'field_name')
                      else "dimension")
        try:
            val = int(v)
            if val < 5:
                print(f"Warning: {field_name} '{v}' is below minimum (5). "
                      f"Clamping to 5.")
                return 5
            if val > 100:
                print(f"Warning: {field_name} '{v}' exceeds maximum (100). "
                      f"Clamping to 100.")
                return 100
            return val
        except (ValueError, TypeError, OverflowError):
            print(f"Invalid type for {field_name}: {v!r}. "
                  f"Using default value (20).")
            return 20


class GameConfigModel(BaseModel):
    """Main configuration model for the Pac-Man game.

    Unknown keys are ignored and every field has a default value, so an
    empty model is always a valid configuration.

    Attributes:
        MIN_LEVELS: Minimum number of levels the game must have.
        PACGUM_RATIO: Ratio used to compute the number of pacgums.
        highscore_filename: Path of the file where high scores are saved.
        levels: Configuration of each level, padded with default levels
            up to MIN_LEVELS.
        lives: Number of lives the player starts with (1 to 10).
        pacgum: Number of pacgums per level, or None to compute it.
        points_per_pacgum: Points awarded for eating a pacgum.
        points_per_super_pacgum: Points awarded for a super pacgum.
        points_per_ghost: Points awarded for eating a ghost.
        seed: Seed for the random number generator.
        level_max_time: Maximum time allowed per level, in seconds.
    """

    MIN_LEVELS: ClassVar[int] = 10
    PACGUM_RATIO: ClassVar[float] = 0.9

    highscore_filename: str = "highscores.json"
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [
            LevelConfig() for _ in range(GameConfigModel.MIN_LEVELS)])
    lives: int = Field(default=3, gt=0, le=10)
    pacgum: int | None = Field(default=None, gt=0)
    points_per_pacgum: int = Field(default=10, gt=0)
    points_per_super_pacgum: int = Field(default=50, gt=0)
    points_per_ghost: int = Field(default=200, gt=0)
    seed: int = Field(default=42, gt=0)
    level_max_time: int = Field(default=90, gt=0)

    @field_validator("levels", mode="after")
    @classmethod
    def ensure_min_levels(cls, v: list[LevelConfig]) -> list[LevelConfig]:
        """Complete the levels with default ones up to MIN_LEVELS.

        Args:
            v: Validated list of levels read from the configuration.

        Returns:
            A new list with at least MIN_LEVELS levels. The input list is
            not modified.
        """

        levels = list(v)
        if len(levels) < cls.MIN_LEVELS:
            print(
                f"Notice: Only {len(levels)} level(s) provided in "
                f"configuration. Padding with default levels up "
                f"to {cls.MIN_LEVELS}."
            )
            while len(levels) < cls.MIN_LEVELS:
                levels.append(LevelConfig())
        return levels


class ConfigParser:
    """Parser for the Pac-Man configuration JSON file using Pydantic.

    Handles comments starting with '#', ignores unknown keys, and clamps
    invalid values to safe defaults according to project specifications.

    Attributes:
        filepath: Path of the JSON configuration file.
        config: Validated game configuration. Falls back to default
            values if the file is missing or malformed.
    """

    def __init__(self, filepath: str) -> None:
        """Initialize the parser and load the configuration file.

        Args:
            filepath: Path of the JSON configuration file to load.
        """

        self.filepath = filepath
        self.config = self._load_and_validate_configuration()

    def _build_model(self, data: dict[str, Any]) -> GameConfigModel:
        """Build the configuration, dropping the keys with invalid values.

        Each invalid key is reported with a message and removed, so the
        default value is used for it. The valid keys are kept. The dict
        given is not modified.

        Args:
            data: Dictionary with the raw configuration read from JSON.

        Returns:
            A validated GameConfigModel. If no invalid key can be
            identified, a model with all default values is returned.
        """

        clean = dict(data)
        while True:
            try:
                return GameConfigModel(**clean)
            except ValidationError as error:
                removed = 0
                for item in error.errors():
                    loc = item["loc"]
                    if not loc:
                        continue
                    key = str(loc[0])
                    if key in clean:
                        print(f"Invalid value for '{key}': {clean[key]!r} "
                              f"({item['msg']}). Using the default value.")
                        clean.pop(key)
                        removed += 1
                if removed == 0:
                    return GameConfigModel()

    def _load_and_validate_configuration(self) -> GameConfigModel:
        """Load the JSON file, strip comments and validate it.

        Lines whose first non-blank character is '#' are replaced by empty
        lines so the line numbers in JSON error messages stay accurate.
        Any problem (missing file, syntax error, wrong root type or
        unexpected exception) is reported and the default configuration
        is returned instead of raising.

        Returns:
            The validated GameConfigModel, or one with default values if
            the file could not be loaded.
        """

        if not os.path.exists(self.filepath):
            print(f"Error: Configuration file '{self.filepath}' not found."
                  f" Using default values.")
            return GameConfigModel()

        try:
            with open(self.filepath, "r", encoding='utf-8') as f:
                lines = f.readlines()

            clean_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    clean_lines.append("\n")
                else:
                    clean_lines.append(line)

            json_str = "".join(clean_lines)
            data = json.loads(json_str)

            if not isinstance(data, dict):
                print("Error: Configuration root must be a JSON object. "
                      "Using defaults.")
                return GameConfigModel()

            return self._build_model(data)

        except json.JSONDecodeError as e:
            print(f"Syntax error in configuration file: {e}. "
                  f"Using default values.")
            return GameConfigModel()
        except Exception as e:
            print(f"Unexpected error reading config: {e}. "
                  f"Using default values.")
            return GameConfigModel()
