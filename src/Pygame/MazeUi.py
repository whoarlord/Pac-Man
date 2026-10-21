import pygame
from mazegenerator import MazeGenerator
from EntitiesAdapter import EntitiesAdapter
from typing import Tuple


class MazeUi:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.width = width
        self.height = height
        self.window_width = 1920
        self.window_height = 1080
        self.margin = 5
        self.thick = 3
        self.lines_color = (255, 255, 255)
        self.cell_size: Tuple[int, int] = self.calculate_cell_size()
        self.initializeMaze()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.window_width, self.window_height))
        self.screen.fill("black")

    def calculate_cell_size(self):
        cell_width = (self.window_width - self.margin) / self.width
        cell_height = (self.window_height - self.margin) / self.height
        return (cell_width, cell_height)

    def saveImage(self, image, name):
        pygame.image.save(image, name)

    def createRect(self, init_x, init_y, finish_x, finish_y, N, E, W, S):
        if (N):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, init_y),
                             (finish_x, init_y), self.thick)
        if (E):
            pygame.draw.line(self.screen, self.lines_color,
                             (finish_x, init_y),
                             (finish_x, finish_y), self.thick)
        if (W):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, init_y),
                             (init_x, finish_y), self.thick)
        if (S):
            pygame.draw.line(self.screen, self.lines_color,
                             (init_x, finish_y),
                             (finish_x, finish_y), self.thick)

    def createMazeBlock(self, cell: int, x: int, y: int,
                        x_increment: int, y_increment: int):
        N = bool(cell & 1)
        E = bool(cell & 2)
        S = bool(cell & 4)
        W = bool(cell & 8)
        self.createRect(x, y, x + x_increment, y + y_increment, N, E, W, S)

    def makeMaze(self, x_cells, y_cells):
        x = self.margin
        y = self.margin
        x_increment = (self.window_width - self.margin) / x_cells
        y_increment = (self.window_height - self.margin) / y_cells
        for i in range(y_cells):
            for j in range(x_cells):
                actual_cell = self.maze.maze[i][j]
                self.createMazeBlock(actual_cell, x, y,
                                     x_increment, y_increment)
                x += x_increment
            x = self.margin
            y += y_increment

    def initializeMaze(self):
        self.maze: MazeGenerator = MazeGenerator((self.width, self.height))
        self.maze.generate()

    def createAllSquaresAndSavingThem(self, x_limit):
        x = 5
        y = 5
        increment = 50
        margin = 10
        for i in range(16):
            self.createMazeBlock(i, x, y, x + increment, y + increment)

            zone = self.screen.subsurface(
                pygame.Rect(x, y, increment + 1, increment + 1)
            ).copy()
            self.saveImage(zone, f"../img/square_{i}.png")
            x += increment + margin
            if (x + increment + margin > x_limit):
                x = 5
                y += increment + margin

    def place_player(self, player: pygame.Surface):
        x = int((self.width - 1) / 2)
        y = int((self.height - 1) / 2)
        print(f"x: {x}")
        print(f"y: {y}")
        self.place_element(player, x, y)

    def place_element(self, element: pygame.Surface, x: int, y: int):
        self.screen.blit(element, self.calculate_rect_for_cell((x, y)))

    def calculate_rect_for_cell(self, cell: Tuple[int, int]):
        x_increment = (self.window_width - self.margin) / self.width
        y_increment = (self.window_height - self.margin) / self.height
        x_coordinate = self.margin + (x_increment * (cell[0]))
        y_coordinate = self.margin + (y_increment * (cell[1]))
        return pygame.Rect(x_coordinate, y_coordinate, x_increment, y_increment)

    def setup_entities(self, entityAdapter: EntitiesAdapter):
        player = entityAdapter.makePlayerImage()
        mazeUi.place_player(player)
        red_ghost = entityAdapter.makeRedGhostImage()
        mazeUi.place_element(red_ghost, 0, 0)
        yellow_ghost = entityAdapter.makeYellowGhostImage()
        mazeUi.place_element(yellow_ghost, 0, self.height - 1)
        blue_ghost = entityAdapter.makeBlueGhostImage()
        mazeUi.place_element(blue_ghost, self.width - 1, 0)
        pink_ghost = entityAdapter.makePinkGhostImage()
        mazeUi.place_element(pink_ghost, self.width - 1, self.height - 1)

    def event_loop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()


if __name__ == '__main__':
    # pygame setup
    mazeUi = MazeUi(20, 20)
    entityAdapter = EntitiesAdapter(mazeUi.cell_size)
    mazeUi.makeMaze(20, 20)
    mazeUi.setup_entities(entityAdapter)
    mazeUi.event_loop()
