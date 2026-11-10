"""Helpers to draw pixel by pixel on pygame surfaces."""

from pygame import (Surface, SRCALPHA)

Cell = tuple[int, int]
Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


class MLXAdapter:
    """Drawing helpers that work pixel by pixel on pygame surfaces.

    Attributes:
        COLORS: Colors that set_color knows by name.
    """

    COLORS: dict[str, Color] = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'orange': (255, 140, 0)
    }

    def draw_line(self, surface: Surface, color: Color,
                  source: Cell, target: Cell, thick: int = 1) -> None:
        """Draw a line between two points.

        Each pixel of the line is drawn as a square of thick x thick
        pixels.

        Args:
            surface: Surface to draw on.
            color: Color of the line.
            source: Start of the line as (x, y).
            target: End of the line as (x, y).
            thick: Thickness of the line in pixels.
        """

        half = thick // 2
        for x, y in self.get_line(list(source), list(target)):
            for dy in range(-half, thick - half):
                for dx in range(-half, thick - half):
                    surface.set_at((x + dx, y + dy), color)

    def get_line(self, source: list[int],  target: list[int]
                 ) -> list[list[int]]:
        """Return the pixels of a line from source to target.

        In each step it moves one pixel on each axis towards the
        target, so the line goes diagonally first and then straight.
        Both ends are included.

        Args:
            source: Start of the line as [x, y].
            target: End of the line as [x, y].

        Returns:
            A list with the pixels as [x, y].
        """

        actual_pixel: list[int] = list(source)
        result_pixels: list[list[int]] = []
        while (actual_pixel != target):
            result_pixels.append(actual_pixel)
            actual_pixel = self.aproximate_coordinates(actual_pixel, target)
        result_pixels.append(target)
        return result_pixels

    def draw_cells(self, surface: Surface, cells: list[Cell],
                   color: Color) -> None:
        """Paint single pixels.

        Args:
            surface: Surface to draw on.
            cells: Pixels to paint as (x, y).
            color: Color of the pixels.
        """

        for cell in cells:
            surface.set_at(cell, color)

    def draw_circle(self, surface: Surface, color: Color,
                    center: Cell, radius: int) -> None:
        """Draw a filled circle.

        Args:
            surface: Surface to draw on.
            color: Color of the circle.
            center: Center as (x, y) in pixels.
            radius: Radius in pixels.
        """

        cx, cy = center
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    surface.set_at((x, y), color)

    @staticmethod
    def aproximate_integers(source: int, target: int) -> int:
        """Move an integer one unit towards another.

        Args:
            source: Integer to move.
            target: Integer to move towards.

        Returns:
            source + 1 if it is lower than target, source - 1 if it is
            higher, and source if they are equal.
        """

        if (source < target):
            return source + 1
        elif (source > target):
            return source - 1
        return source

    def aproximate_coordinates(self, source: list[int],
                               target: list[int]
                               ) -> list[int]:
        """Move a point one pixel towards another on each axis.

        Args:
            source: Point to move as [x, y].
            target: Point to move towards as [x, y].

        Returns:
            The new point as [x, y].
        """

        result: list[int] = [0, 0]
        result[0] = self.aproximate_integers(source[0], target[0])
        result[1] = self.aproximate_integers(source[1], target[1])
        return result

    @staticmethod
    def distance(a: Cell, b: Cell) -> int:
        """Return the Manhattan distance between two cells.

        Args:
            a: First cell as (x, y).
            b: Second cell as (x, y).

        Returns:
            The sum of the differences of the columns and the rows.
        """

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def scale_image(src: Surface, size: tuple[int, int]) -> Surface:
        """Scale a surface to a size, pixel by pixel.

        Each pixel of the new image copies the nearest pixel of the
        original, so the colors are not mixed.

        Args:
            src: Surface to scale.
            size: New size as (width, height).

        Returns:
            A new surface with per-pixel alpha.
        """

        new_w, new_h = size
        old_w, old_h = src.get_size()
        dst = Surface((new_w, new_h), SRCALPHA)
        for y in range(new_h):
            src_y = y * old_h // new_h
            for x in range(new_w):
                src_x = x * old_w // new_w
                dst.set_at((x, y), src.get_at((src_x, src_y)))
        return dst

    @staticmethod
    def set_alpha(src: Surface, alpha: int) -> None:
        """Set the alpha of every pixel of a surface.

        It writes directly in the buffer of the surface, so it expects
        4 bytes per pixel with the alpha in the fourth one. The surface
        is modified.

        Args:
            src: Surface to modify.
            alpha: New alpha, from 0 to 255.
        """

        buf = src.get_buffer()
        data = bytearray(buf.raw)
        n = len(data) // 4
        data[3::4] = bytes([alpha]) * n
        buf.write(bytes(data), 0)
        del buf

    def set_color(self, src: Surface, color: str) -> None:
        """Fill a surface with a color, keeping its alpha.

        It writes directly in the buffer of the surface, using the
        masks of the surface to find the position of each channel.

        Args:
            src: Surface to modify.
            color: Name of a color in COLORS. An unknown name gives
                black.
        """

        r, g, b = self.COLORS.get(color, (0, 0, 0))
        buf = src.get_buffer()
        data = bytearray(buf.raw)
        masks = src.get_masks()
        for value, mask in zip((r, g, b), masks[:3]):
            offset = mask.bit_length() // 8 - 1
            data[offset::4] = bytes([value]) * (len(data) // 4)
        buf.write(bytes(data), 0)
        del buf
