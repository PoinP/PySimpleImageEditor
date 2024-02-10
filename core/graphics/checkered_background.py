"""
Used to construct checkered patterns. Mainly used for
the construction of a pattern similar to the one shown
on the alpha channel of transperent images
"""
from PIL import ImageDraw
from PIL import Image as PILImage

from core.graphics.image import Image


class CheckeredBackground(Image):
    def __init__(self, size: tuple[int, int],
                 main_color: str = "white",
                 secondary_color: str = "grey") -> None:
        self.__size = size
        self.__main_color = main_color
        self.__secondary_color = secondary_color

        image = PILImage.new("RGB", size, main_color)
        draw = ImageDraw.Draw(image)

        TILE_SIZE = 10

        for i in range(0, size[1], TILE_SIZE):
            for j in range(0, size[0], TILE_SIZE):
                if (i // TILE_SIZE) % 2 == (j // TILE_SIZE) % 2:
                    width = j + TILE_SIZE
                    height = i + TILE_SIZE
                    draw.rectangle([i, j, height, width], fill=secondary_color)

        super().__init__(image=image, mode="RGB")
