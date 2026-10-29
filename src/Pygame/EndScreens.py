import sys
import os
import json
import pygame
from typing import Any
from src.Config.ConfigParser import GameConfigModel


class EndScreenBase:
    def __init__(self, screen: pygame.Surface, config: GameConfigModel,
                 score: int) -> None:
        self.screen = screen
        self.config = config
        self.final_score = score
        self.player_name = ""
        self.font_title = pygame.font.Font(None, 80)
        self.font_options = pygame.font.Font(None, 50)
        self.font_text = pygame.font.Font(None, 36)
        self.running = True
        self.confirm_overwrite = False
        self.existing_score = 0
        self.save_failed = False

    def _load_scores(self) -> list[dict[str, Any]]:
        filename = self.config.highscore_filename
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except OSError:
            return []
        except ValueError:
            data = None
        if isinstance(data, list):
            return data
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

    def _find_entry(self, name: str) -> dict[str, Any] | None:
        name_clean = name.strip()

        for entry in self._load_scores():
            if not isinstance(entry, dict):
                continue
            registered_name = str(entry.get("name", "")).strip()
            if registered_name == name_clean:
                return entry
        return None

    @staticmethod
    def _get_score(entry: dict[str, Any]) -> int:
        try:
            val = entry.get("score", 0)
            return int(float(val))
        except (ValueError, TypeError, OverflowError):
            return 0

    def _save_highscore(self) -> bool:
        filename = self.config.highscore_filename
        name_to_save = self.player_name.strip()
        if not name_to_save:
            name_to_save = "PLAYER"

        scores_list = [
            entry for entry in self._load_scores()
            if isinstance(entry, dict)
            and str(entry.get("name", "")).strip() != name_to_save
        ]
        scores_list.append({"name": name_to_save, "score": self.final_score})
        scores_list.sort(key=self._get_score, reverse=True)
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

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    name_to_check = self.player_name.strip()
                    if not name_to_check:
                        name_to_check = "PLAYER"
                    entry = self._find_entry(name_to_check)
                    if entry is not None and not self.confirm_overwrite:
                        self.existing_score = self._get_score(entry)
                        self.confirm_overwrite = True
                    elif self.save_failed or self._save_highscore():
                        self.running = False
                    else:
                        self.save_failed = True
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                    self.confirm_overwrite = False
                elif len(self.player_name) < 10:
                    if event.unicode.isalnum() or event.key == pygame.K_SPACE:
                        self.player_name += event.unicode
                        self.confirm_overwrite = False

    def _draw_overwrite_warning(self) -> None:
        width = self.screen.get_width()
        if self.save_failed:
            lines = ["The score could not be saved (see the terminal).",
                     "Press ENTER to continue."]
        elif self.confirm_overwrite:
            name = self.player_name.strip()
            if not name:
                name = "PLAYER"
            lines = [
                f"That name already exists as: {name} "
                f"{self.existing_score} pts.",
                "Press ENTER to overwrite it, or change the name."
            ]
        else:
            return
        for i, line in enumerate(lines):
            surface = self.font_text.render(line, True, (255, 50, 50))
            self.screen.blit(surface,
                             ((width - surface.get_width()) // 2,
                              630 + i * 35))


class GameOverScreen(EndScreenBase):
    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        width = self.screen.get_width()

        title = self.font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title, ((width - title.get_width()) // 2, 250))

        score_text = self.font_options.render(f"Final Score: "
                                              f"{self.final_score} pts",
                                              True, (255, 255, 255))
        self.screen.blit(score_text, ((width - score_text.get_width()) // 2,
                                      380))

        prompt = self.font_text.render("Enter your name:", True, (255, 238, 0))
        self.screen.blit(prompt, ((width - prompt.get_width()) // 2, 500))

        display_name = self.player_name if self.player_name else "_"
        name_surface = self.font_options.render(display_name, True,
                                                (0, 255, 255))
        self.screen.blit(name_surface, ((width - name_surface.get_width()
                                         ) // 2, 560))

        self._draw_overwrite_warning()

        info = self.font_text.render(
            "[ Press ENTER to Save & Return to "
            "Menu ]", True, (150, 150, 150))
        self.screen.blit(info, ((width - info.get_width()) // 2, 720))

        pygame.display.flip()

    def run(self) -> bool:
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)
        return True


class VictoryScreen(EndScreenBase):

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        width = self.screen.get_width()

        title = self.font_title.render("VICTORY!", True, (0, 255, 0))
        self.screen.blit(title, ((width - title.get_width()) // 2, 250))

        score_text = self.font_options.render(f"Final Score: "
                                              f"{self.final_score} pts", True,
                                              (255, 255, 255))
        self.screen.blit(score_text, ((width - score_text.get_width()) // 2,
                                      380))

        prompt = self.font_text.render("Enter your name:", True, (255, 238, 0))
        self.screen.blit(prompt, ((width - prompt.get_width()) // 2, 500))

        display_name = self.player_name if self.player_name else "_"
        name_surface = self.font_options.render(display_name, True,
                                                (0, 255, 255))
        self.screen.blit(name_surface, ((width - name_surface.get_width()
                                         ) // 2, 560))

        self._draw_overwrite_warning()

        info = self.font_text.render(
            "[ Press ENTER to Save & Return to "
            "Menu ]", True, (150, 150, 150))
        self.screen.blit(info, ((width - info.get_width()) // 2, 720))

        pygame.display.flip()

    def run(self) -> bool:
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)
        return True
