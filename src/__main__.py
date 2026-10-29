import sys
import pygame
from src.Config.ConfigParser import ConfigParser
from src.Entities.EntityFactory import EntityFactory
from src.Pygame.MazeUi import MazeUi
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Pygame.Menu import MainMenu
from src.Pygame.EndScreens import GameOverScreen, VictoryScreen


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

        try:
            mazeUi = MazeUi(parser.config)
        except pygame.error as e:
            print(f"Pygame error: Could not initialize the graphics display "
                  f"({e}).", file=sys.stderr)
            sys.exit(1)

        menu = MainMenu(mazeUi.screen, parser.config)

        while True:
            menu.state = "MAIN"
            menu.run()

            mazeUi.reset()

            entityAdapter = EntitiesAdapter((int(mazeUi.cell_size[0]),
                                            int(mazeUi.cell_size[1])))
            mazeUi.entity_factory = entityFactory
            mazeUi.entity_adapter = entityAdapter

            mazeUi.load_level(0)
            mazeUi.setup_entities()

            mazeUi.event_loop()

            if mazeUi.player.lives <= 0:
                end_screen = GameOverScreen(mazeUi.screen, parser.config,
                                            mazeUi.player.score)
                mazeUi.back_to_menu = end_screen.run()
            elif not mazeUi.pacgums and (mazeUi.current_level + 1 >= len
                                         (parser.config.levels)):
                victory_screen = VictoryScreen(mazeUi.screen, parser.config,
                                               mazeUi.player.score)
                mazeUi.back_to_menu = victory_screen.run()

            if not mazeUi.back_to_menu:
                break
    except KeyboardInterrupt:
        print("\nJuego cerrado limpiamente por el usuario (Ctrl+C).")
    except (FileNotFoundError, pygame.error) as e:
        print(f"Error: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        exit_code = 1
    finally:
        pygame.quit()
    sys.exit(exit_code)
