import pygame
from typing import Tuple


class EntitiesAdapter:
    def __init__(self, entity_dimensions: Tuple[int, int]):
        self.img_route = "src/img/"
        self.entity_dimensions = entity_dimensions

    def _load_entity(self, route: str):
        img = pygame.image.load(route).convert_alpha()
        return pygame.transform.scale(img, self.entity_dimensions)

    def makePlayerImage(self):
        return self._load_entity(f"{self.img_route}pacman.png")

    def makeRedGhostImage(self):
        return self._load_entity(f"{self.img_route}red_ghost.png")

    def makeYellowGhostImage(self):
        return self._load_entity(f"{self.img_route}yellow_ghost.png")

    def makeBlueGhostImage(self):
        return self._load_entity(f"{self.img_route}blue_ghost.png")

    def makePinkGhostImage(self):
        return self._load_entity(f"{self.img_route}pink_ghost.png")
