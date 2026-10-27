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
        self.show_error = False
        self.error_message = "The name already exists. ¡Choose another one!"

    def _load_scores(self) -> list[dict[str, Any]]:
        filename = self.config.highscore_filename
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    def _name_exists(self, name: str) -> bool:
        scores = self._load_scores()
        name_clean = name.strip()

        for entry in scores:
            registered_name = entry.get("name", "")
            registered_name_clean = registered_name.strip()
            if registered_name_clean == name_clean:
                return True
        return False

    def _save_highscore(self) -> None:
        filename = self.config.highscore_filename
        name_to_save = self.player_name.strip()
        if not name_to_save:
            name_to_save = "PLAYER"

        scores_list = self._load_scores()
        scores_list.append({"name": name_to_save, "score": self.final_score})
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(scores_list, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving highscores: {e}")

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
                    if self._name_exists(name_to_check):
                        self.show_error = True
                    else:
                        self._save_highscore()
                        self.running = False
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                    self.show_error = False
                elif len(self.player_name) < 10:
                    if event.unicode.isalnum() or event.key == pygame.K_SPACE:
                        self.player_name += event.unicode
                        self.show_error = False


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

        if self.show_error:
            error_surface = self.font_text.render(self.error_message, True,
                                                  (255, 50, 50))
            self.screen.blit(error_surface, ((width - error_surface.get_width()
                                              ) // 2, 630))

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

        if self.show_error:
            error_surface = self.font_text.render(self.error_message, True,
                                                  (255, 50, 50))
            self.screen.blit(error_surface, ((width - error_surface.get_width()
                                              ) // 2, 630))

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
