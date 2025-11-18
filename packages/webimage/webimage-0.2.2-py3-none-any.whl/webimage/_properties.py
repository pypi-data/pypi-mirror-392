from attrs import define, field, validators

from webimage._typing import ImageHeight, ImageWidth


@define
class ImageSize:
    """
    Represents the size of an image.

    Attributes:
        width: The width of the image in pixels.
        height: The height of the image in pixels.
    """

    width: ImageWidth
    height: ImageHeight


@define
class ImageProperties:
    """
    Represents the properties of an image.

    Attributes:
        filename: The name of the image file.
        size: The size of the image as a tuple of (width, height).
        img_format: The PIL format of the image (e.g., "JPEG", "PNG", "WebP").
        mode: The mode of the image (e.g., "RGB", "RGBA").
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
        prepend_path: The string that will be concatenated in front of the image name in the `srcset` attribute.
        image_name: The name of the image file.
        width: The width of the image in pixels.
        format: The format of the image (e.g., "webp","jpg", "png").
    """

    prepend_path: str
    image_name: str
    width: ImageWidth
    img_format: str = "webp"

    def __str__(self) -> str:
        return f"{self.prepend_path}{self.image_name}.{self.img_format} {self.width}w"


@define
class Sizes:
    """
    Represents the `sizes` attribute for responsive images.

    Attributes:
        max_vw_width: The maximum viewport width in pixels.
        img_vw_width: The width of the image in viewport width units (vw).
        max_img_px_width: The maximum image width in pixels (for viewports larger than `max_vw_width`).
    """

    max_viewport_width: ImageWidth
    img_vw_width: int = field(validator=validators.in_(range(1, 101)))
    max_img_px_width: ImageWidth

    def __str__(self) -> str:
        return f"(max-width: {self.max_viewport_width}px) {self.img_vw_width}vw, {self.max_img_px_width}px"
