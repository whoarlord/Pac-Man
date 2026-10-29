import sys
import pygame
from src.Config.ConfigParser import ConfigParser
from src.Entities.EntityFactory import EntityFactory
from src.Pygame.MazeUi import MazeUi
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Pygame.Menu import MainMenu
from src.Pygame.MazeGrid import MazeGrid
from src.Pygame.MazeRenderer import MazeRenderer


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 -m src <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if not config_path.lower().endswith(".json"):
        print(f"Received: '{config_path}', expected a '.json' file",
              file=sys.stderr)
        sys.exit(1)

    parser = ConfigParser(config_path)
    entityFactory = EntityFactory()

    mazeUi = MazeUi(parser.config)
    width, height = mazeUi.get_actual_level_size()
    maze_grid = MazeGrid(width, height)
    entity_adapter = EntitiesAdapter(maze_grid.get_cell_size())
    maze_renderer = MazeRenderer(maze_grid, mazeUi, entity_adapter)
    menu = MainMenu(maze_renderer.screen, parser.config)

    while True:
        menu.state = "MAIN"
        menu.run()

        maze_renderer.reset()
        maze_renderer.setup_entities()
        maze_renderer.event_loop()

        if not mazeUi.back_to_menu:
            break

    pygame.quit()
    sys.exit(1)
