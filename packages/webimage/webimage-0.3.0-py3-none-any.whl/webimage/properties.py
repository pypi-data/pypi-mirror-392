from enum import Enum

from attrs import define, field, validators

from webimage._typing import ImageHeight, ImageWidth


@define
class ImageSize:
    """
    Represents the size of an image.

    Attributes:
        width (ImageWidth): The width of the image in pixels.
        height (ImageHeight): The height of the image in pixels.
    """

    width: ImageWidth
    height: ImageHeight


@define
class ImageProperties:
    """
    Represents the properties of an image.

    Attributes:
        filename (str): The name of the image file.
        size (ImageSize): The size of the image as a tuple of (width, height).
        img_format (str): The PIL format of the image (e.g., "JPEG", "PNG", "WebP").
        mode (str): The mode of the image (e.g., "RGB", "RGBA").
    """

    filename: str
    size: ImageSize
    img_format: str
    mode: str


@define
class SrcsetItem:
    """
    Represents an item in the `srcset` attribute.

    Attributes:
        prepend_path (str): The string that will be concatenated in front of the image name in the `srcset` attribute.
        image_name (str): The name of the image file.
        width (ImageWidth): The width of the image in pixels.
        img_format (str): The format of the image (e.g., "webp","jpg", "png").
    """

    prepend_path: str
    image_name: str
    width: ImageWidth
    img_format: str = "webp"

    def __str__(self) -> str:
        return f"{self.prepend_path}{self.image_name}.{self.img_format} {self.width}w"


@define
class MediaCondition:
    """
    Represents the media conditions for responsive images. Typically used in the `sizes` HTML attribute.

    Attributes:
        min_or_max_width (Literal["min", "max"]): Whether to use "min-width" or "max-width" in the media query.
        width_of_window (ImageWidth): Value of min-width or max-width in pixels for the media query.
        image_width (int): The width of the image.
        image_unit (Literal["vw", "px"]): The unit for the image width (either "vw" or "px").
    """

    min_or_max_width: str = field(default="max", validator=validators.in_(["min", "max"]))
    width_of_window: ImageWidth = field(default=1050)
    image_width: int = field(default=800)
    image_unit: str = field(default="px", validator=validators.in_(["vw", "px"]))

    def __str__(self) -> str:
        return f"({self.min_or_max_width}-width: {self.width_of_window}px) {self.image_width}{self.image_unit}"


@define
class Sizes:
    """
    Represents the `sizes` attribute for responsive images.

    Should iterate over the list of `MediaConditions` and return a string representation for the `sizes` attribute
    that looks something like this:

    ```
    (min-width: 1050px) 800px,
    (min-width: 675px) 620px,
     96vw
    ```

    Attributes:
        media_conditions (list[MediaConditions]): A list of `MediaConditions` instances that represent the media queries and their corresponding image widths.
        default_width (int): The default width of image when no media conditions are met.
        default_unit (str): The unit for the default width (either "vw" or "px").
    """

    media_conditions: list[MediaCondition] = field(factory=MediaCondition)
    default_width: int = field(default=97)
    default_unit: str = field(default="vw", validator=validators.in_(["vw", "px"]))

    def __str__(self) -> str:
        media_conditions_str = ",\n".join(str(condition) for condition in self.media_conditions)
        return f"{media_conditions_str},\n\t\t\t\t{self.default_width}{self.default_unit}"


class ScaleSizes(Enum):
    """Will scale images to indicated width (height will be auto adjusted)."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    THUMB = "thumbnail"

    @property
    def width(self) -> ImageWidth:
        if self == ScaleSizes.SMALL:
            return 350
        elif self == ScaleSizes.MEDIUM:
            return 600
        elif self == ScaleSizes.LARGE:
            return 1200
        elif self == ScaleSizes.THUMB:
            return 150
        else:
            raise ValueError(f"Invalid scale size: {self.value}")

    @property
    def height(self) -> ImageHeight:
        return "auto"
