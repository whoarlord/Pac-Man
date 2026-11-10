"""Images of the Pac-Man entities and icons, loaded and cached."""

import os
import pygame
from typing import Tuple
from src.Entities.MovementEntity import MovingDirection
from src.Ui.MLXAdapter import MLXAdapter


class EntitiesAdapter:
    """Gives the images of the entities, scaled to the size of the cells.

    The images are read from the img folder, which is one level above
    the folder of this file.

    Attributes:
        ICON_SIZE: Size in pixels (width, height) of the icons.
        img_route: Path of the folder with the images, ending in a
            separator.
        entity_dimensions: Size in pixels (width, height) of the images
            of the entities.
        pacman_state: Number of the animation frame of the player, from
            5 to 1.
        calls_counter: Calls to makePlayerImage since the animation
            frame last changed.
        cache: Loaded images, by route.
        mlx_adapter: Adapter used to scale the images.
    """

    ICON_SIZE = (76, 38)

    def __init__(self, entity_dimensions: Tuple[int, int]) -> None:
        """Create the adapter.

        Args:
            entity_dimensions: Size in pixels (width, height) of the
                images of the entities.
        """

        img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "img")
        self.img_route = os.path.normpath(img_dir) + os.sep
        self.entity_dimensions = entity_dimensions
        self.pacman_state = 5
        self.calls_counter: int = 0
        self.cache: dict[str, pygame.Surface] = {}
        self.mlx_adapter = MLXAdapter()

    def _all_image_routes(self) -> list[str]:
        """Return the route of every image the game needs.

        Returns:
            A list with the paths of the PNG files.
        """

        names = [
            "scared_ghost", "red_ghost", "yellow_ghost", "blue_ghost",
            "pink_ghost", "invincible_icon_low", "pacman_down_1",
            "pacman_down_2", "pacman_down_3", "pacman_down_4", "pacman_down_5",
            "pacman_left_1", "pacman_left_2", "pacman_left_3", "pacman_left_4",
            "pacman_left_5", "pacman_right_1", "pacman_right_2",
            "pacman_right_3", "pacman_right_4", "pacman_right_5",
            "pacman_up_1", "pacman_up_2", "pacman_up_3", "pacman_up_4",
            "pacman_up_5", "extra_live", "speed_up", "ghost_freeze"
        ]
        return [f"{self.img_route}{name}.png" for name in names]

    def preload_images(self) -> None:
        """Load all the images into the cache.

        Raises:
            FileNotFoundError: If any image is missing. The message
                lists all the missing ones.
            pygame.error: If an image cannot be loaded.
        """

        routes = self._all_image_routes()
        missing = [route for route in routes if not os.path.isfile(route)]
        if missing:
            raise FileNotFoundError(
                "Missing image files: " + ", ".join(missing))
        for route in routes:
            self._load_entity(route)

    def _get_pacman_image(self, direction: MovingDirection) -> str:
        """Return the route of the player image for a direction.

        It uses the current animation frame. NOT_MOVING uses the image
        for right.

        Args:
            direction: Direction of the player.

        Returns:
            The path of the image.
        """

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
        """Load an image scaled to entity_dimensions, using the cache.

        Args:
            route: Path of the image.

        Returns:
            The scaled image.

        Raises:
            pygame.error: If the image cannot be loaded.
        """

        if route in self.cache:
            return self.cache[route]
        try:
            img = pygame.image.load(route)
        except pygame.error as e:
            raise pygame.error(f"Cannot load image '{route}': {e}") from e
        scaled = self.mlx_adapter.scale_image(img, self.entity_dimensions)
        self.cache[route] = scaled
        return scaled

    def _load_icon(self, route: str) -> pygame.Surface:
        """Load an image scaled to ICON_SIZE, using the cache.

        Args:
            route: Path of the image.

        Returns:
            The scaled image.

        Raises:
            pygame.error: If the image cannot be loaded.
        """

        key = f"icon:{route}"
        if key in self.cache:
            return self.cache[key]
        try:
            img = pygame.image.load(route)
        except pygame.error as e:
            raise pygame.error(f"Cannot load image '{route}': {e}") from e
        scaled = self.mlx_adapter.scale_image(img, self.ICON_SIZE)
        self.cache[key] = scaled
        return scaled

    def makePlayerImage(self, direction: MovingDirection) -> pygame.Surface:
        """Return the image of the player for a direction.

        Every third call it also moves the animation to the next frame
        (5, 4, 3, 2, 1 and back to 5).

        Args:
            direction: Direction of the player.

        Returns:
            The image of the player.
        """

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
        """Return the image of a scared ghost."""

        return self._load_entity(f"{self.img_route}scared_ghost.png")

    def makeRedGhostImage(self, scared: bool = False) -> pygame.Surface:
        """Return the image of the red ghost.

        Args:
            scared: If True, the image of a scared ghost is returned.

        Returns:
            The image of the ghost.
        """

        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}red_ghost.png")

    def makeYellowGhostImage(self, scared: bool = False) -> pygame.Surface:
        """Return the image of the yellow ghost.

        Args:
            scared: If True, the image of a scared ghost is returned.

        Returns:
            The image of the ghost.
        """

        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}yellow_ghost.png")

    def makeBlueGhostImage(self, scared: bool = False) -> pygame.Surface:
        """Return the image of the blue ghost.

        Args:
            scared: If True, the image of a scared ghost is returned.

        Returns:
            The image of the ghost.
        """

        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}blue_ghost.png")

    def makePinkGhostImage(self, scared: bool = False) -> pygame.Surface:
        """Return the image of the pink ghost.

        Args:
            scared: If True, the image of a scared ghost is returned.

        Returns:
            The image of the ghost.
        """

        if scared:
            return self.makeScaredGhostImage()
        return self._load_entity(f"{self.img_route}pink_ghost.png")

    def make_invincible_icon(self) -> pygame.Surface:
        """Return the icon of the invincibility, scaled to ICON_SIZE."""

        return self._load_icon(f"{self.img_route}invincible_icon_low.png")

    def make_extra_live_icon(self) -> pygame.Surface:
        """Return the extra life image, scaled to entity_dimensions."""

        return self._load_entity(f"{self.img_route}extra_live.png")

    def make_speed_up_icon(self) -> pygame.Surface:
        """Return the icon of the speed boost, scaled to ICON_SIZE."""

        return self._load_icon(f"{self.img_route}speed_up.png")

    def make_ghost_freeze_icon(self) -> pygame.Surface:
        """Return the icon of the ghost freeze, scaled to ICON_SIZE."""

        return self._load_icon(f"{self.img_route}ghost_freeze.png")

    def resize(self, entity_dimensions: Tuple[int, int]) -> None:
        """Change the size of the images of the entities.

        The cache is cleared (icons included) and all the images are
        loaded again.

        Args:
            entity_dimensions: New size in pixels (width, height).

        Raises:
            FileNotFoundError: If any image is missing.
            pygame.error: If an image cannot be loaded.
        """

        self.entity_dimensions = entity_dimensions
        self.cache.clear()
        self.preload_images()
