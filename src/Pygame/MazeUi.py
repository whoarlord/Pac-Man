import pygame
from mazegenerator import MazeGenerator


class MazeUi:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.lines_color = (255, 255, 255)
        self.thick = 3
        self.initializeMaze()
        self.window_width = 1920
        self.window_height = 1080
        self.margin = 5
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.window_width, self.window_height))
        self.screen.fill("black")

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
                print(f"actual cell: {actual_cell}")
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


if __name__ == '__main__':
    # pygame setup
    pygame.init()
    mazeUi = MazeUi(20, 20)
    clock = pygame.time.Clock()
    running = True

    mazeUi.makeMaze(20, 20)
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()