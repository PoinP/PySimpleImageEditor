"""
A simple wrapper of some of the functionality that PIL
offers. It makes editing pictures easier and enables
for e distructionless editing of the pictures
"""

import copy
from dataclasses import dataclass

from PIL import ImageOps
from PIL import Image as PILImage
from PIL import ImageTk, ImageEnhance
from PIL import UnidentifiedImageError


@dataclass
class _Properties:
    resize: tuple[int, int] = (0, 0)
    offset: tuple[int, int] = (0, 0)
    crop: tuple[int, int, int, int] = (0, 0, 0, 0)
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


class ImageNotRecognizedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Image:
    def __init__(self, path: str | None = None,
                 image: PILImage.Image | None = None,
                 mode: str | None = None) -> None:
        self.__image = None

        if path is not None:
            try:
                self.__image = PILImage.open(path).convert("RGBA")
                self.__image.load()
            except UnidentifiedImageError as e:
                raise ImageNotRecognizedError(*e.args)

        if image is not None and path is None:
            self.__image = image.copy()

        self.__reference = self.__image.copy()
        self.__mode = mode if mode is not None else "RGBA"

        self.__props = _Properties()
        self.__props.resize = self.get_size()

    def save(self, path: str, format: (str | None) = None) -> None:
        self.__image.save(path, format)

    def copy(self) -> "Image":
        copy_image = Image(image=self.__reference.copy())
        copy_image.__mode = self.__mode
        copy_image.__props = copy.deepcopy(self.__props)
        copy_image.__apply_all_properties()
        return copy_image

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
    def paste(self, image: "Image", box: tuple[int, int] | None = None) -> None: # noqa
        mask = image.__image
        self.__image.paste(image.__image, box, mask)

    def cropped_paste(self, image: "Image", box: tuple[int, int] | None = None) -> None: # noqa
        width, height = image.get_size()
        ref_width, ref_height = image.__reference.size

        width_offset = ref_width // 2 - width // 2
        height_offset = ref_height // 2 - height // 2
        offset_box = (width_offset, height_offset)

        if box is not None:
            offset_box = (box[0] + offset_box[0], box[1] + offset_box[1])

        self.paste(image, offset_box)

    def shrink_to_fit(self, canvas_size: tuple[int, int]) -> None:
        resample = PILImage.Resampling.BICUBIC
        self.__image.thumbnail(canvas_size, resample)
        self.__reference.thumbnail(canvas_size, resample)
        self.__props.resize = self.__reference.size
        self.__apply_all_properties()

    def center(self, canvas_size: tuple[int, int]) -> None:
        width, height = self.__props.resize
        canvas_width, canvas_height = canvas_size

        x, y = width // 2, height // 2
        canvas_x, canvas_y = (canvas_width // 2, canvas_height // 2)

        x_offset = canvas_x - x
        y_offset = canvas_y - y

        self.__props.offset = (x_offset, y_offset)

    def replace(self, image: "Image"):
        self.paste(image)
        self.__props = copy.deepcopy(image.__props)

    def clear(self) -> None:
        self.__image = PILImage.new(self.__mode, self.get_size())
        self.__reference = self.__image.copy()
        self.__props = _Properties()

    def reset(self) -> None:
        self.__image = self.__reference.copy()

    def clear_effects(self) -> None:
        old_offset = self.__props.offset
        self.__props = _Properties()
        self.__props.offset = old_offset
        self.__props.resize = self.__reference.size
        self.__apply_all_properties()

    def rotate(self, angle: float) -> None:
        self.__props.rotation = angle
        self.__apply_all_properties()

    def resize(self, size: tuple[int | None, int | None]) -> None:
        if size == (None, None):
            return

        x, y = size
        curr_x, curr_y = self.__props.resize

        x = x or curr_x
        y = y or curr_y

        size = (x, y)
        self.__props.resize = size
        self.__apply_all_properties()

    def set_offset(self, offset: tuple[int | None, int | None]) -> None:
        x, y = self.__props.offset
        x_offset, y_offset = offset

        x_offset = x_offset or 0
        y_offset = y_offset or 0

        self.__props.offset = (x + x_offset, y + y_offset)

    def scale(self, scale: tuple[float | None, float | None]) -> None:
        x, y = self.__props.resize
        scale_x, scale_y = scale

        scale_x = scale_x or 1.0
        scale_y = scale_y or 1.0

        size = (int(x * scale_x), int(y * scale_y))
        self.resize(size)

    def crop(self, crop: tuple[int | None, int | None,
                               int | None, int | None]) -> None:
        x, y, xx, yy = self.__props.crop
        crop_x, crop_y, crop_xx, crop_yy = crop

        crop_x = crop_x or 0
        crop_y = crop_y or 0
        crop_xx = crop_xx or 0
        crop_yy = crop_yy or 0

        crop = (x + crop_x, y + crop_y, xx + crop_xx, yy + crop_yy)

        width, height = self.__props.resize

        if crop[0] + crop[2] >= width or crop[1] + crop[3] >= height:
            return

        self.__props.crop = crop
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
        self.__mode = "RGB"
        self.__reference = self.__reference.convert("RGB")
        self.__reference = ImageOps.invert(self.__reference).convert("RGBA")
        self.__apply_all_properties()

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
        self.__reference = self.__reference.convert(mode).convert("RGBA")
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

        if props.flip_horizontal:
            image = image.transpose(PILImage.Transpose.FLIP_LEFT_RIGHT)
        if props.flip_vertical:
            image = image.transpose(PILImage.Transpose.FLIP_TOP_BOTTOM)

        if props.resize != self.__reference.size:
            resample = PILImage.Resampling.BICUBIC
            image = image.resize(props.resize, resample, reducing_gap=True)

        if props.crop != (0, 0, 0, 0):
            x, y, xx, yy = 0, 0, *props.resize
            crop_x, crop_y, crop_xx, crop_yy = props.crop
            crop = (x + crop_x, y + crop_y, xx - crop_xx, yy - crop_yy)
            image = image.crop(crop)

        if props.rotation != 0:
            resample = PILImage.Resampling.BICUBIC
            image = image.rotate(props.rotation, resample, expand=True)

        self.__image = image
