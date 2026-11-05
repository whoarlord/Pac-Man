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


if __name__ == '__main__':
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
        entityFactory = EntityFactory()

        while True:
            mazeUi = MazeUi(parser.config)

            width, height = mazeUi.get_actual_level_size()
            maze_grid = MazeGrid(width, height)

            entity_adapter = EntitiesAdapter(maze_grid.get_cell_size())

            maze_renderer = MazeRenderer(maze_grid, mazeUi, entity_adapter)
            entity_adapter.preload_images()

            menu = MainMenu(maze_renderer.screen, parser.config)

            menu.state = "MAIN"
            menu.run()

            # mazeUi.reset()
            maze_renderer.setup_entities()
            maze_renderer.load_first_level()
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
        exit_code = 1
    finally:
        pygame.quit()
    sys.exit(exit_code)
