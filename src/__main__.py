"""Main entry point of the Pac-Man game.

This module validates the command-line arguments, loads the configuration
file and runs the game loop: main menu, gameplay and end screens
(game over or victory). The loop restarts every time the player chooses
to go back to the menu from an end screen.
"""

import sys
import pygame
import traceback
from src.Config.ConfigParser import ConfigParser
from src.Game.GameState import GameState
from src.Ui.EntitiesAdapter import EntitiesAdapter
from src.Ui.Menu import MainMenu
from src.Ui.MazeGrid import MazeGrid
from src.Ui.MazeRenderer import MazeRenderer
from src.Ui.EndScreens import GameOverScreen, VictoryScreen
from src.Game.LevelLoader import LevelLoader
from src.Game.GameRules import GameRules
from src.Game.MovementController import MovementController
from src.Game.GameController import GameController


def main() -> None:
    """Run the Pac-Man game from the command line.

    Reads the path of a JSON configuration file from ``sys.argv``, parses
    it and builds every component the game needs (state, grid, renderer,
    menu, level loader, rules and controllers). It then shows the main
    menu, runs the game and displays the proper end screen depending on
    the outcome:

    * Game over screen if the player has no lives left.
    * Victory screen if every pacgum was eaten on the last level.

    The whole cycle repeats while the player chooses to go back to the
    menu. Pygame is always shut down before the program exits.

    Raises:
        SystemExit: Always raised at the end of the function. The exit
            code is 0 on a normal or user-requested (Ctrl+C) exit, and 1
            if the arguments are invalid, a file is missing, pygame
            fails or any unexpected error occurs.

    Note:
        ``KeyboardInterrupt``, ``FileNotFoundError``, ``pygame.error`` and
        any other ``Exception`` are caught internally and reported on
        stdout or stderr, so they never propagate to the caller.
    """

    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if not config_path.lower().endswith(".json"):
        print(f"Received: '{config_path}', expected a '.json' file",
              file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    try:
        parser = ConfigParser(config_path)

        while True:
            game_state = GameState(parser.config)

            width, height = game_state.get_actual_level_size()
            maze_grid = MazeGrid(width, height)

            entity_adapter = EntitiesAdapter(maze_grid.get_cell_size())

            maze_renderer = MazeRenderer(maze_grid, game_state, entity_adapter)
            entity_adapter.preload_images()

            menu = MainMenu(maze_renderer.screen, parser.config)

            menu.state = "MAIN"
            menu.run()

            level_loader = LevelLoader(game_state, maze_grid, entity_adapter)
            game_rules = GameRules(game_state, maze_grid, level_loader)
            movement_controller = MovementController(game_state, maze_grid,
                                                     entity_adapter)

            game_controller = GameController(
                game_state=game_state,
                renderer=maze_renderer,
                level_loader=level_loader,
                rules=game_rules,
                movement_controller=movement_controller
            )

            level_loader.setup_entities()
            level_loader.load_first_level()

            game_controller.run()

            if game_state.player.lives <= 0:
                end_screen = GameOverScreen(maze_renderer.screen,
                                            parser.config,
                                            game_state.player.score)
                game_state.back_to_menu = end_screen.run()
            elif (not game_state.pacgums
                    and not game_state.super_pacgums
                    and game_state.current_level + 1
                    >= len(parser.config.levels)):
                victory_screen = VictoryScreen(maze_renderer.screen,
                                               parser.config,
                                               game_state.player.score)
                game_state.back_to_menu = victory_screen.run()

            if not game_state.back_to_menu:
                break
    except KeyboardInterrupt:
        print("\nGame closed cleanly by the user (Ctrl+C).")
    except (FileNotFoundError, pygame.error) as e:
        print(f"Error: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        traceback.print_exc()
        exit_code = 1
    finally:
        pygame.quit()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
