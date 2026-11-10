from pygame import (Surface, SRCALPHA)

Cell = tuple[int, int]
Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


class MLXAdapter:
    COLORS: dict[str, Color] = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'orange': (255, 140, 0)
    }

    def draw_line(self, surface: Surface, color: Color,
                  source: Cell, target: Cell, thick: int = 1):
        half = thick // 2
        for x, y in self.get_line(list(source), list(target)):
            for dy in range(-half, thick - half):
                for dx in range(-half, thick - half):
                    surface.set_at((x + dx, y + dy), color)

    def get_line(self, source: list[int],  target: list[int]
                 ) -> list[list[int]]:
        actual_pixel: list[int] = list(source)
        result_pixels: list[list[int]] = []
        while (actual_pixel != target):
            result_pixels.append(actual_pixel)
            actual_pixel = self.aproximate_coordinates(actual_pixel, target)
        result_pixels.append(target)
        return result_pixels

    def draw_cells(self, surface: Surface, cells: list[Cell],
                   color: Color) -> None:
        for cell in cells:
            surface.set_at(cell, color)

    def draw_circle(self, surface: Surface, color: Color,
                    center: Cell, radius: int) -> None:
        cx, cy = center
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    surface.set_at((x, y), color)

    @staticmethod
    def aproximate_integers(source: int, target: int) -> int:
        if (source < target):
            return source + 1
        elif (source > target):
            return source - 1
        return source

    def aproximate_coordinates(self, source: list[int],
                               target: list[int]
                               ) -> list[int]:
        result: list[int] = [0, 0]
        result[0] = self.aproximate_integers(source[0], target[0])
        result[1] = self.aproximate_integers(source[1], target[1])
        return result

    @staticmethod
    def distance(a: Cell, b: Cell) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def scale_image(src: Surface, size: tuple[int, int]) -> Surface:
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
        buf = src.get_buffer()
        data = bytearray(buf.raw)
        n = len(data) // 4
        data[3::4] = bytes([alpha]) * n
        buf.write(bytes(data), 0)
        del buf

    def set_color(self, src: Surface, color: str) -> None:
        r, g, b = self.COLORS.get(color, (0, 0, 0))
        buf = src.get_buffer()
        data = bytearray(buf.raw)
        masks = src.get_masks()
        print(masks)
        for value, mask in zip((r, g, b), masks[:3]):
            print(mask.bit_length())
            offset = mask.bit_length() // 8 - 1
            data[offset::4] = bytes([value]) * (len(data) // 4)
        buf.write(bytes(data), 0)
        del buf
