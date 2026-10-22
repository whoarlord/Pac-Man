import os
import json
from typing import Any, List, ClassVar
from pydantic import BaseModel, Field, ValidationError, field_validator


class LevelConfig(BaseModel):
    """Configuration model for a single game level dimensions."""

    # ge=5: "Greater than or equal to 5" (el ancho y alto mínimo son 5)
    width: int = Field(default=20, ge=5)
    height: int = Field(default=20, ge=5)

    @field_validator("width", "height", mode="before")
    @classmethod
    def validate_dimensions(cls, v: Any) -> int:
        """Ensure dimensions are valid positive integers, clamping if needed.
        """

        try:
            val = int(v)
            # Clamping: acotamos el valor para que nunca sea
            # inferior a 5 de forma segura
            return max(5, val)
        except (ValueError, TypeError):
            return 20


class GameConfigModel(BaseModel):
    """Main configuration model for the Pac-Man game."""

    # Minimum number of levels the game must have.
    MIN_LEVELS: ClassVar[int] = 10

    highscore_filename: str = "highscores.json"
    # Un objeto LevelConfig nuevo por cada nivel por defecto.
    # default_factory con lambda: evita compartir referencias de listas
    # en memoria y genera una lista nueva con un nivel por defecto si no
    # viene especificado en el JSON.
    levels: List[LevelConfig] = Field(
        default_factory=lambda: [
            LevelConfig() for _ in range(GameConfigModel.MIN_LEVELS)])
    # gt=0: "Greater than 0" (estrictamente mayor que 0,
    # no se permiten vidas <= 0)
    lives: int = Field(default=3, gt=0)
    # ge=0: "Greater than or equal to 0" (no se permiten cantidades negativas)
    pacgum: int = Field(default=42, gt=0)
    points_per_pacgum: int = Field(default=10, gt=0)
    points_per_super_pacgum: int = Field(default=50, gt=0)
    points_per_ghost: int = Field(default=200, gt=0)
    seed: int = 42
    # gt=0: El tiempo máximo por nivel debe ser estrictamente mayor que 0
    level_max_time: int = Field(default=90, gt=0)

    @field_validator("levels", mode="after")
    @classmethod
    def ensure_min_levels(cls, v: list[LevelConfig]) -> list[LevelConfig]:
        """Complete the levels with default ones up to MIN_LEVELS."""

        levels = list(v)
        if len(levels) < cls.MIN_LEVELS:
            print(f"Only {len(levels)} level(s) in the configuration: "
                  f"adding default levels up to {cls.MIN_LEVELS}.")
            while len(levels) < cls.MIN_LEVELS:
                levels.append(LevelConfig())
        return levels


class ConfigParser:
    """Parser for the Pac-Man configuration JSON file using Pydantic.

    Handles comments starting with '#', ignores unknown keys, and clamps
    invalid values to safe defaults according to project specifications.
    """

    def __init__(self, filepath: str) -> None:
        """Initialize the parser and load the configuration file."""

        self.filepath = filepath
        self.config = self._load_and_validate_configuration()

    _load_configuration = None

    def _build_model(self, data: dict[str, Any]) -> GameConfigModel:
        """Build the configuration, dropping the keys with invalid values.

        Each invalid key is reported with a message and removed, so the
        default value is used for it. The valid keys are kept. The dict
        given is not modified.
        """

        # Trabajamos con una copia para no modificar el dict de fuera.
        clean = dict(data)
        while True:
            try:
                # **clean desempaqueta el diccionario y se lo pasa a
                # Pydantic, que valida tipos y aplica valores por defecto.
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
                # Si no se ha borrado ninguna clave, volver a intentarlo
                # fallaría para siempre: usamos todo por defecto.
                if removed == 0:
                    return GameConfigModel()

    def _load_and_validate_configuration(self) -> GameConfigModel:
        """Loads the JSON, strips comments, and validates it using Pydantic."""

        if not os.path.exists(self.filepath):
            print(f"Error: Configuration file '{self.filepath}' not found."
                  f" Using default values.")
            return GameConfigModel()

        try:
            with open(self.filepath, "r", encoding='utf-8') as f:
                lines = f.readlines()

            # Filtrar líneas vacías y comentarios que empiezan por '#'
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

            # Pydantic ignora las claves desconocidas, y _build_model se
            # encarga de los valores inválidos clave por clave.
            return self._build_model(data)

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error in configuration file: {e}. "
                  f"Using safe default values.")
            return GameConfigModel()
        except Exception as e:
            print(f"Unexpected error reading config: {e}. "
                  f"Using default values.")
            return GameConfigModel()
