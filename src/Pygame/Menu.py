import sys
import os
import json
import pygame
from typing import Any
from src.Config.ConfigParser import GameConfigModel


class MainMenu:
    def __init__(self, screen: pygame.Surface, config: GameConfigModel):
        self.screen = screen
        self.config = config
        self.font_title = pygame.font.Font(None, 80)
        self.font_options = pygame.font.Font(None, 50)
        self.font_text = pygame.font.Font(None, 36)
        self.options = ["Start Game", "View Highscores",
                        "Instructions", "Exit"]
        self.selected_index = 0
        self.state = "MAIN"

    def _draw_main_menu(self) -> None:
        screen_width = self.screen.get_width()
        text_surface = self.font_title.render("PAC-MAN", True, (255, 238, 0))
        x_centre = (screen_width - text_surface.get_width()) // 2
        self.screen.blit(text_surface, (x_centre, 150))

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                color = (255, 255, 255)
            else:
                color = (100, 100, 100)

            option_surface = self.font_options.render(option, True, color)

            x_option = (screen_width - option_surface.get_width()) // 2
            y_option = 350 + i * 80

            self.screen.blit(option_surface, (x_option, y_option))

    def _draw_instructions(self) -> None:
        screen_width = self.screen.get_width()
        title_surface = self.font_title.render("GAME INSTRUCTIONS",
                                               True, (255, 100, 255))
        x_title = (screen_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (x_title, 100))

        lines = [
            "CONTROLS:",
            "• Use ARROW KEYS or W/A/S/D to move Pac-Man.",
            "",
            "RULES:",
            "• Eat all the small Pac-gums to clear the level.",
            "• Eat Super Pac-gums to turn ghosts vulnerable and eat them!",
            "• Avoid ghosts when they are in their normal state.",
            "• Complete each level before the timer reaches 0."
        ]

        for i, line in enumerate(lines):
            color = (255, 255, 255) if line.startswith("•") else (255, 238, 0)
            line_surface = self.font_text.render(line, True, color)
            x_pos = (screen_width - line_surface.get_width()) // 2
            self.screen.blit(line_surface, (x_pos, 250 + i * 45))

        back_surface = self.font_text.render("[ Press ESC to return to Menu ]",
                                             True, (150, 150, 150))
        x_back = (screen_width - back_surface.get_width()) // 2
        self.screen.blit(back_surface, (x_back, 850))

    def _get_scores(self, element: dict[str, Any]) -> int:
        if isinstance(element, dict):
            return int(element.get("score", 0))
        return 0

    def _draw_highscores(self) -> None:
        screen_width = self.screen.get_width()
        title_surface = self.font_title.render("TOP 10 HIGHSCORES",
                                               True, (0, 255, 255))
        x_title = (screen_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (x_title, 100))

        scores_list = []
        filename = self.config.highscore_filename

        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        scores_list = sorted(data, key=self._get_scores,
                                             reverse=True)
            except Exception:
                pass

        if not scores_list:
            no_score_surface = self.font_text.render(
                "No highscores recorded yet!", True, (150, 150, 150))
            x_no = (screen_width - no_score_surface.get_width()) // 2
            self.screen.blit(no_score_surface, (x_no, 400))
        else:
            for i, entry in enumerate(scores_list[:10]):
                name = entry.get("name", "UNKNOWN")[:10]
                score = entry.get("score", 0)

                line_text = f"{i + 1}. {name:<12} {score:>6} pts"
                score_surface = self.font_text.render(line_text, True,
                                                      (255, 184, 174))
                x_pos = (screen_width - score_surface.get_width()) // 2
                self.screen.blit(score_surface, (x_pos, 220 + i * 45))

        back_surface = self.font_text.render(
            "[ Press ESC to return to Menu ]", True, (150, 150, 150))
        x_back = (screen_width - back_surface.get_width()) // 2
        self.screen.blit(back_surface, (x_back, 850))

    def _execute_option(self) -> str | None:
        selected = self.options[self.selected_index]
        if selected == "Start Game":
            return "START_GAME"
        elif selected == "View Highscores":
            self.state = "HIGHSCORES"
        elif selected == "Instructions":
            self.state = "INSTRUCTIONS"
        elif selected == "Exit":
            pygame.quit()
            sys.exit()
        return None

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        if self.state == "MAIN":
            self._draw_main_menu()
        elif self.state == "HIGHSCORES":
            self._draw_highscores()
        elif self.state == "INSTRUCTIONS":
            self._draw_instructions()

        pygame.display.flip()

    def handle_events(self) -> str | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MAIN"
                if self.state == "MAIN":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_index = ((self.selected_index - 1) %
                                               len(self.options))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_index = ((self.selected_index + 1) %
                                               len(self.options))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return self._execute_option()
        return None

    def run(self) -> None:
        clock = pygame.time.Clock()

        while True:
            action = self.handle_events()
            if action == "START_GAME":
                break
            self.draw()
            clock.tick(60)
