from . import EntityFactory, MazeUi, EntitiesAdapter

if __name__ == '__main__':
    entityFactory = EntityFactory()
    mazeUi = MazeUi(20, 20)
    entityAdapter = EntitiesAdapter(mazeUi.cell_size)
    mazeUi.makeMaze(20, 20)
    mazeUi.setup_entities(entityAdapter, entityFactory)
    mazeUi.event_loop()
