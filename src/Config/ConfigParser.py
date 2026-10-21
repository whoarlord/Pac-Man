import os
import json
from typing import List
from pydantic import BaseModel, Field, ValidationError


class LevelConfig(BaseModel):
    width: int = 20
    height: int = 20


class GameConfigModel(BaseModel):
    highscore_filename: str = "highscores.json"
    levels: List[LevelConfig] = Field(default_factory=lambda: [LevelConfig()])
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90


class ConfigParser:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.config = self._load_and_validate_configuration()

    _load_configuration = None

    def _load_and_validate_configuration(self) -> GameConfigModel:
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
                if stripped and not stripped.startswith('#'):
                    clean_lines.append(line)

            json_str = "".join(clean_lines)
            data = json.loads(json_str)

            if not isinstance(data, dict):
                print("Error: Configuration root must be a JSON object. "
                      "Using defaults.")
                return GameConfigModel()

            return GameConfigModel(**data)

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error in configuration file: {e}. "
                  f"Using safe default values.")
            return GameConfigModel()
        except Exception as e:
            print(f"Unexpected error reading config: {e}. "
                  f"Using default values.")
            return GameConfigModel()
