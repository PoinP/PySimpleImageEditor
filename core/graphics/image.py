from PIL import ImageOps
from PIL import Image as PILImage
from PIL import ImageTk, ImageEnhance

from dataclasses import dataclass


@dataclass
class _Properties:
    rotation: float = 0.0
    brightness: float = 1.0
    contrast: float = 1.0
    sharpness: float = 1.0
    saturation: float = 1.0
    flip_vertical: bool = False
    flip_horizontal: bool = False


@dataclass
class _Enchancers:
    brightness: ImageEnhance._Enhance
    contrast: ImageEnhance._Enhance
    sharpness: ImageEnhance._Enhance
    saturation: ImageEnhance._Enhance


class Image:
    def __init__(self, path: str | None = None,
                 image: PILImage.Image | None = None,
                 mode: str | None = None) -> None:
        # TODO: Handle error
        self.__original_image = None
        self.__image = None

        if path is not None:
            self.__original_image = PILImage.open(path).convert("RGBA")
            self.__original_image.load()

        if image is not None and path is None:
            self.__original_image = image

        resample = PILImage.Resampling.BICUBIC
        self.__image = self.__original_image.copy()
        self.__image.thumbnail([500, 500], resample)

        self.__reference = self.__image.copy()
        self.__mode = mode if mode is not None else "RGBA"

        self.__props = _Properties()

    def save(self, path: str, format: (str | None) = None) -> None:
        self.__image.save(path, format)

    def copy(self) -> "Image":
        return Image(image=self.__image)

    #    Accessors    #
    def get_base_image(self) -> PILImage:
        return self.__image

    def get_size(self) -> (int, int):
        return self.__image.size

    def get_tkinter_data(self) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(self.__image)

    def get_properties(self) -> _Properties:
        return self.__props

    def get_thumbnail(self, size: tuple[int, int]) -> "Image":
        resample = PILImage.Resampling.BICUBIC
        thumbnail_image = self.__image.copy()
        thumbnail_image.thumbnail(size, resample)
        return Image(image=thumbnail_image)

    #    Converters    #
    def convert_to_rgb(self) -> None:
        self.__convert("RGB")

    def convert_to_rgba(self) -> None:
        self.__convert("RGBA")

    def convert_to_grayscale(self) -> None:
        if self.__mode == "RGB":
            self.__convert("L")
        else:
            self.__convert("LA")

    #    Modifiers    #
    def paste(self, image: "Image", box: tuple | None = None) -> None:
        self.__image.paste(image.__image, box, image.__image)
        # self.__reference = self.__image.copy()

    def cropped_paste(self, image: "Image", box: tuple | None = None) -> None:
        width, height = image.get_size()
        ref_width, ref_height = image.__reference.size

        width_offset = ref_width // 2 - width // 2
        height_offset = ref_height // 2 - height // 2
        offset_box = (width_offset, height_offset)

        if box is not None:
            offset_box = (box[0] + offset_box[0], box[1], offset_box[1])

        self.paste(image, offset_box)

    def clear(self) -> None:
        self.__image = PILImage.new(self.__mode, self.get_size())
        self.__reference = self.__image.copy()

    def reset(self) -> None:
        self.__image = self.__reference.copy()

    def rotate(self, angle: float) -> None:
        self.__props.rotation = angle
        self.__apply_all_properties()

    def flip_horizontal(self) -> None:
        should_flip = not self.__props.flip_horizontal
        self.__props.flip_horizontal = should_flip
        self.__apply_all_properties()

    def flip_vertical(self) -> None:
        should_flip = not self.__props.flip_vertical
        self.__props.flip_vertical = should_flip
        self.__apply_all_properties()

    def apply_brightness(self, coefficient: float) -> None:
        self.__props.brightness = coefficient
        self.__apply_all_properties()

    def apply_contrast(self, coefficient: float) -> None:
        self.__props.contrast = coefficient
        self.__apply_all_properties()

    def apply_sharpness(self, coefficient: float) -> None:
        self.__props.sharpness = coefficient
        self.__apply_all_properties()

    def apply_saturation(self, coefficient: float) -> None:
        self.__props.saturation = coefficient
        self.__apply_all_properties()

    def apply_negative(self) -> None:
        # TODO: FIX
        self.__image = ImageOps.invert(self.__image)

    def print_data(self) -> None:
        width = self.__image.width
        height = self.__image.height
        pixels = list(self.__image.getdata())

        data = [pixels[i:i+width] for i in range(0, len(pixels), height)]
        print(data)

    #    Private Methods    #
    def __convert(self, mode: str) -> None:
        if self.__mode == mode:
            return

        self.__mode = mode
        self.__reference = self.__reference.convert(mode)
        self.__apply_all_properties()

    def __apply_all_properties(self) -> None:
        props = self.__props
        image = self.__reference.copy()
        enhancers = _Enchancers(
            ImageEnhance.Brightness(image),
            ImageEnhance.Contrast(image),
            ImageEnhance.Sharpness(image),
            ImageEnhance.Color(image),
        )

        if props.brightness != 1.0:
            image.paste(enhancers.brightness.enhance(props.brightness))
        if props.contrast != 1.0:
            image.paste(enhancers.contrast.enhance(props.contrast))
        if props.sharpness != 1.0:
            image.paste(enhancers.sharpness.enhance(props.sharpness))
        if props.saturation != 1.0:
            image.paste(enhancers.saturation.enhance(props.saturation))

        if props.rotation != 0:
            resample = PILImage.Resampling.BICUBIC
            image = image.rotate(props.rotation, resample, expand=True)

        if props.flip_horizontal:
            image = image.transpose(PILImage.Transpose.FLIP_TOP_BOTTOM)
        if props.flip_vertical:
            image = image.transpose(PILImage.Transpose.FLIP_LEFT_RIGHT)

        self.__image = image
