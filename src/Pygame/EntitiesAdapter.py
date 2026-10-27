import pygame
from typing import Tuple
from src.Entities.MovementEntity import MovingDirection


class EntitiesAdapter:
    def __init__(self, entity_dimensions: Tuple[int, int]) -> None:
        self.img_route = "src/img/"
        self.entity_dimensions = entity_dimensions
        self.pacman_state = 5
        self.calls_counter: int = 0

    def _get_pacman_image(self, direction: MovingDirection) -> str:
        if direction is MovingDirection.MOVING_UP:
            return f'{self.img_route}pacman_up_{self.pacman_state}.png'
        elif direction is MovingDirection.MOVING_DOWN:
            return f'{self.img_route}pacman_down_{self.pacman_state}.png'
        elif (direction is MovingDirection.MOVING_RIGHT
                or direction is MovingDirection.NOT_MOVING):
            return f'{self.img_route}pacman_right_{self.pacman_state}.png'
        elif direction is MovingDirection.MOVING_LEFT:
            return f'{self.img_route}pacman_left_{self.pacman_state}.png'

    def _load_entity(self, route: str) -> pygame.Surface:
        img = pygame.image.load(route).convert_alpha()
        return pygame.transform.scale(img, self.entity_dimensions)

    def makePlayerImage(self, direction: MovingDirection) -> pygame.Surface:
        img = self._get_pacman_image(direction)
        if self.calls_counter >= 2:
            self.calls_counter = 0
            if (self.pacman_state == 1):
                self.pacman_state = 5
            else:
                self.pacman_state -= 1
        else:
            self.calls_counter += 1
        return self._load_entity(img)

    def makeScaredGhostImage(self):
        return self._load_entity(f"{self.img_route}scared_ghost.png")

    def makeRedGhostImage(self, scared: bool = False):
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}red_ghost.png")

    def makeYellowGhostImage(self, scared: bool = False):
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}yellow_ghost.png")

    def makeBlueGhostImage(self, scared: bool = False):
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}blue_ghost.png")

    def makePinkGhostImage(self, scared: bool = False):
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}pink_ghost.png")
