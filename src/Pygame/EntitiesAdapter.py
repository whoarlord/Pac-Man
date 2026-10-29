import os
import pygame
from typing import Tuple
from src.Entities.MovementEntity import MovingDirection


class EntitiesAdapter:
    def __init__(self, entity_dimensions: Tuple[int, int]) -> None:
        img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "img")
        self.img_route = os.path.normpath(img_dir) + os.sep
        self.entity_dimensions = entity_dimensions
        self.pacman_state = 5
        self.calls_counter: int = 0
        self.cache: dict[str, pygame.Surface] = {}
        self._preload_images()

    def _all_image_routes(self) -> list[str]:
        names = [
            "scared_ghost", "red_ghost", "yellow_ghost", "blue_ghost",
            "pink_ghost", "invincible_icon_low", "pacman_down_1",
            "pacman_down_2", "pacman_down_3", "pacman_down_4", "pacman_down_5",
            "pacman_left_1", "pacman_left_2", "pacman_left_3", "pacman_left_4",
            "pacman_left_5", "pacman_right_1", "pacman_right_2",
            "pacman_right_3", "pacman_right_4", "pacman_right_5",
            "pacman_up_1", "pacman_up_2", "pacman_up_3", "pacman_up_4",
            "pacman_up_5"
        ]
        return [f"{self.img_route}{name}.png" for name in names]

    def _preload_images(self) -> None:
        routes = self._all_image_routes()
        missing = [route for route in routes if not os.path.isfile(route)]
        if missing:
            raise FileNotFoundError(
                "Missing image files: " + ", ".join(missing))
        for route in routes:
            self._load_entity(route)

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
        if route in self.cache:
            return self.cache[route]
        try:
            img = pygame.image.load(route).convert_alpha()
        except pygame.error as e:
            raise pygame.error(f"Cannot load image '{route}': {e}") from e
        scaled = pygame.transform.scale(img, self.entity_dimensions)
        self.cache[route] = scaled
        return scaled

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

    def makeScaredGhostImage(self) -> pygame.Surface:
        return self._load_entity(f"{self.img_route}scared_ghost.png")

    def makeRedGhostImage(self, scared: bool = False) -> pygame.Surface:
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}red_ghost.png")

    def makeYellowGhostImage(self, scared: bool = False) -> pygame.Surface:
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}yellow_ghost.png")

    def makeBlueGhostImage(self, scared: bool = False) -> pygame.Surface:
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}blue_ghost.png")

    def makePinkGhostImage(self, scared: bool = False) -> pygame.Surface:
        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}pink_ghost.png")

    def make_invincible_icon(self) -> pygame.Surface:
        return self._load_entity(f"{self.img_route}invincible_icon_low.png")
