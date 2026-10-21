import sys
from .Config.ConfigParser import ConfigParser
from . import EntityFactory, MazeUi, EntitiesAdapter

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 -m src <config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    parser = ConfigParser(config_path)

    levels = parser.config.levels
    width = levels[0].width if levels else 20
    height = levels[0].height if levels else 20

    entityFactory = EntityFactory()
    mazeUi = MazeUi(width, height)
    entityAdapter = EntitiesAdapter(mazeUi.cell_size)
    mazeUi.makeMaze(width, height)
    mazeUi.setup_entities(entityAdapter, entityFactory)
    mazeUi.event_loop()
