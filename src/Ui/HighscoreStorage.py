"""Reading and writing of the highscores file."""

import os
import json
from typing import Any
from src.Config.ConfigParser import GameConfigModel


class HighscoreStorage:
    """Loads and saves the highscores in a JSON file.

    The file name is config.highscore_filename. It contains a list of
    entries, each one a dictionary with the keys 'name' and 'score'.

    Attributes:
        config: Configuration of the game.
    """

    def __init__(self, config: GameConfigModel) -> None:
        """Create the storage.

        Args:
            config: Configuration of the game.
        """

        self.config = config

    def load_scores(self) -> list[dict[str, Any]]:
        """Load the highscores from the file.

        If the file is not valid JSON, cannot be read or does not
        contain a list, it is treated as malformed (see
        _malformed_highscore). Entries that are not dictionaries are
        ignored.

        Returns:
            The entries sorted from the highest to the lowest score. The
            list is empty if the file does not exist or is malformed.
        """

        filename = self.config.highscore_filename
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except ValueError:
            self._malformed_highscore(filename)
            return []
        except OSError:
            if os.path.isfile(filename):
                self._malformed_highscore(filename)
            return []
        if isinstance(data, list):
            valid = [entry for entry in data if isinstance(entry, dict)]
            return sorted(valid, key=self.get_score, reverse=True)
        self._malformed_highscore(filename)
        return []

    @staticmethod
    def _malformed_highscore(filename: str) -> None:
        """Rename a malformed highscores file to malformed_highscore.txt.

        It prints a warning. If the file cannot be renamed, it prints a
        different warning instead of raising.

        Args:
            filename: Path of the malformed file.
        """

        backup = "malformed_highscore.txt"
        try:
            os.replace(filename, backup)
            print(f"Warning: '{filename}' is not valid. "
                  f"A copy was saved as '{backup}'.")
        except OSError as e:
            print(f"Warning: could not back up '{filename}': {e}")

    def find_entry(self, name: str) -> dict[str, Any] | None:
        """Find the entry of a player.

        The names are compared without the spaces at the start and the
        end.

        Args:
            name: Name of the player.

        Returns:
            The entry, or None if the name is not in the highscores.
        """

        name_clean = name.strip()

        for entry in self.load_scores():
            if not isinstance(entry, dict):
                continue
            registered_name = str(entry.get("name", "")).strip()
            if registered_name == name_clean:
                return entry
        return None

    @staticmethod
    def get_score(entry: dict[str, Any]) -> int:
        """Return the score of an entry as an integer.

        A missing or invalid score counts as 0.

        Args:
            entry: Entry with the keys 'name' and 'score'.

        Returns:
            The score as an int.
        """

        try:
            val = entry.get("score", 0)
            return int(float(val))
        except (ValueError, TypeError, OverflowError):
            return 0

    def save_highscore(self, player_name: str, final_score: int) -> bool:
        """Save a score, keeping only the best 10.

        The name is stripped and, if it is empty, PLAYER is used. An
        entry with the same name is replaced, even if its score was
        higher. The file is written to a temporary file (the filename
        plus '.tmp') that then replaces the real one.

        Args:
            player_name: Name of the player.
            final_score: Score of the player.

        Returns:
            True if it was saved, False if there was an error (which is
            printed).
        """

        filename = self.config.highscore_filename
        name_to_save = player_name.strip()
        if not name_to_save:
            name_to_save = "PLAYER"

        scores_list = [
            entry for entry in self.load_scores()
            if isinstance(entry, dict)
            and str(entry.get("name", "")).strip() != name_to_save
        ]
        scores_list.append({"name": name_to_save, "score": final_score})
        scores_list.sort(key=self.get_score, reverse=True)
        top_scores = scores_list[:10]
        tmp_filename = filename + ".tmp"
        try:
            with open(tmp_filename, "w", encoding="utf-8") as f:
                json.dump(top_scores, f, indent=4, ensure_ascii=False)
            os.replace(tmp_filename, filename)
        except Exception as e:
            print(f"Error saving highscores: {e}")
            return False
        return True
