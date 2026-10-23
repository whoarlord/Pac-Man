import sys
from .Config.ConfigParser import ConfigParser
from . import EntityFactory, MazeUi, EntitiesAdapter

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
    entityAdapter = EntitiesAdapter(mazeUi.cell_size)
    mazeUi.makeMaze(mazeUi.width, mazeUi.height)
    mazeUi.setup_entities(entityAdapter, entityFactory)
    mazeUi.event_loop()
