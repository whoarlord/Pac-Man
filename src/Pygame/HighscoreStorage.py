import os
import json
from typing import Any
from src.Config.ConfigParser import GameConfigModel


class HighscoreStorage:
    def __init__(self, config: GameConfigModel) -> None:
        self.config = config

    def load_scores(self) -> list[dict[str, Any]]:
        filename = self.config.highscore_filename
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return []
        if isinstance(data, list):
            valid = [entry for entry in data if isinstance(entry, dict)]
            return sorted(valid, key=self.get_score, reverse=True)
        self._malformed_highscore(filename)
        return []

    @staticmethod
    def _malformed_highscore(filename: str) -> None:
        backup = "malformed_highscore.txt"
        try:
            os.replace(filename, backup)
            print(f"Warning: '{filename}' is not valid. "
                  f"A copy was saved as '{backup}'.")
        except OSError as e:
            print(f"Warning: could not back up '{filename}': {e}")

    def find_entry(self, name: str) -> dict[str, Any] | None:
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
        try:
            val = entry.get("score", 0)
            return int(float(val))
        except (ValueError, TypeError, OverflowError):
            return 0

    def save_highscore(self, player_name: str, final_score: int) -> bool:
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
