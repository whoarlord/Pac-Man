import sys
import pygame
from src.Config.ConfigParser import ConfigParser
from src.Entities.EntityFactory import EntityFactory
from src.Pygame.MazeUi import MazeUi
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Pygame.Menu import MainMenu
from src.Pygame.MazeGrid import MazeGrid
from src.Pygame.MazeRenderer import MazeRenderer
from src.Pygame.EndScreens import GameOverScreen, VictoryScreen
import traceback


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 -m src <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if not config_path.lower().endswith(".json"):
        print(f"Received: '{config_path}', expected a '.json' file",
              file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    try:
        parser = ConfigParser(config_path)
        entityFactory = EntityFactory()

        while True:
            print("maze Ui")
            mazeUi = MazeUi(parser.config)
            print("width")
            width, height = mazeUi.get_actual_level_size()
            maze_grid = MazeGrid(width, height)
            print("maze grid")
            entity_adapter = EntitiesAdapter(maze_grid.get_cell_size())
            print("maze renderer")
            maze_renderer = MazeRenderer(maze_grid, mazeUi, entity_adapter)
            entity_adapter.preload_images()
            print("menu")
            menu = MainMenu(maze_renderer.screen, parser.config)

            menu.state = "MAIN"
            print("urning menu")
            menu.run()

            # mazeUi.reset()
            print("settting entities")
            maze_renderer.setup_entities()
            print("loading first level")
            maze_renderer.load_first_level()
            print("event_loop")
            maze_renderer.event_loop()

            if mazeUi.player.lives <= 0:
                end_screen = GameOverScreen(maze_renderer.screen,
                                            parser.config,
                                            mazeUi.player.score)
                mazeUi.back_to_menu = end_screen.run()
            elif (not maze_renderer.pacgums
                    and not maze_renderer.super_pacgums
                    and mazeUi.current_level + 1
                    >= len(parser.config.levels)):
                victory_screen = VictoryScreen(maze_renderer.screen,
                                               parser.config,
                                               mazeUi.player.score)
                mazeUi.back_to_menu = victory_screen.run()

            if not mazeUi.back_to_menu:
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


""" except pygame.error as e:
        print(f"Pygame error: Could not initialize the graphics display "
                f"({e}).", file=sys.stderr)
        sys.exit(1) """