from . import EntityFactory
from Pygame import (MazeUi, EntitiesAdapter)

if __name__ == '__main__':
    factory = EntityFactory()
    mazeUi = MazeUi(20, 20)
    entityAdapter = EntitiesAdapter(mazeUi.cell_size)
    mazeUi.event_loop()
