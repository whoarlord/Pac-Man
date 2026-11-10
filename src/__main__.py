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
            gameState = GameState(parser.config)

            width, height = gameState.get_actual_level_size()
            maze_grid = MazeGrid(width, height)

            entity_adapter = EntitiesAdapter(maze_grid.get_cell_size())

            maze_renderer = MazeRenderer(maze_grid, gameState, entity_adapter)
            entity_adapter.preload_images()

            menu = MainMenu(maze_renderer.screen, parser.config)

            menu.state = "MAIN"
            menu.run()

            level_loader = LevelLoader(gameState, maze_grid, entity_adapter)
            game_rules = GameRules(gameState, maze_grid, level_loader)
            movement_controller = MovementController(gameState, maze_grid,
                                                     entity_adapter)

            game_controller = GameController(
                game_state=gameState,
                renderer=maze_renderer,
                level_loader=level_loader,
                rules=game_rules,
                movement_controller=movement_controller
            )

            level_loader.setup_entities()
            level_loader.load_first_level()

            game_controller.run()

            if gameState.player.lives <= 0:
                end_screen = GameOverScreen(maze_renderer.screen,
                                            parser.config,
                                            gameState.player.score)
                gameState.back_to_menu = end_screen.run()
            elif (not gameState.pacgums
                    and not gameState.super_pacgums
                    and gameState.current_level + 1
                    >= len(parser.config.levels)):
                victory_screen = VictoryScreen(maze_renderer.screen,
                                               parser.config,
                                               gameState.player.score)
                gameState.back_to_menu = victory_screen.run()

            if not gameState.back_to_menu:
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
