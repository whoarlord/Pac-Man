import sys
import pygame
from src.Config.ConfigParser import ConfigParser
from src.Entities.EntityFactory import EntityFactory
from src.Pygame.MazeUi import MazeUi
from src.Pygame.EntitiesAdapter import EntitiesAdapter
from src.Pygame.Menu import MainMenu


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

        if not mazeUi.back_to_menu:
            break

    pygame.quit()
    sys.exit(1)
