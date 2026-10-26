import pygame
from typing import Tuple
from src.Entities import MovingDirection


class EntitiesAdapter:
    def __init__(self, entity_dimensions: Tuple[int, int]):
        self.img_route = "src/img/"
        self.entity_dimensions = entity_dimensions
        self.player_images = {
            MovingDirection.NOT_MOVING: f'{self.img_route}pacman_left.png',
            MovingDirection.MOVING_UP: f'{self.img_route}pacman_up.png',
            MovingDirection.MOVING_DOWN: f'{self.img_route}pacman_down.png',
            MovingDirection.MOVING_LEFT: f'{self.img_route}pacman_left.png',
            MovingDirection.MOVING_RIGHT: f'{self.img_route}pacman_right.png',
        }

    def _load_entity(self, route: str):
        img = pygame.image.load(route).convert_alpha()
        return pygame.transform.scale(img, self.entity_dimensions)

    def makePlayerImage(self, direction: MovingDirection):
        img = self.player_images.get(direction)
        return self._load_entity(img)

    def makeRedGhostImage(self):
        return self._load_entity(f"{self.img_route}red_ghost.png")

    def makeYellowGhostImage(self):
        return self._load_entity(f"{self.img_route}yellow_ghost.png")

    def makeBlueGhostImage(self):
        return self._load_entity(f"{self.img_route}blue_ghost.png")

    def makePinkGhostImage(self):
        return self._load_entity(f"{self.img_route}pink_ghost.png")
