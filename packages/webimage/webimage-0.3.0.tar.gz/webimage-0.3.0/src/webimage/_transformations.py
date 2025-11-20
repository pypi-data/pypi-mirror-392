from os import PathLike
from pathlib import Path
from typing import Literal

from attrs import define, field
from PIL import Image, ImageOps, UnidentifiedImageError

from .properties import ImageProperties, ImageSize


@define
class Mage:
    """Magically inspects and transforms images. And by magically, it means using Pillow.

    Attributes:
        file (PathLike): The path to the image file to be transformed.
        output_dir (PathLike): The directory where the transformed image will be saved.
        img_format (str): The format of the output image (e.g., "webp", "jpg"). Default is "webp".
        prefix_name (str): A string to be prefixed to the output file name.
        suffix_name (str): A string to be suffixed to the output file name.
    """

    file: PathLike = field(kw_only=True)
    output_dir: PathLike | None = field(default=None, kw_only=True)
    img_format: str = field(default="webp", kw_only=True)
    prefix_name: str = field(default="", kw_only=True)
    suffix_name: str = field(default="", kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not Path(self.file).is_file():
            raise ValueError(f"Invalid file path: {self.file}")
        if not self._is_image:
            raise ValueError(f"File is not a valid image: {self.file}")
        if not self.output_dir:
            self.output_dir = Path(self.file).parent

    @property
    def _is_image(self) -> bool:
        try:
            with Image.open(self.file) as img:
                return img.format.lower() in ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
        except UnidentifiedImageError:
            return False

    @property
    def _output_path(self) -> Path:
        output_dir = Path(self.output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        output_file = f"{self.prefix_name}{Path(self.file).stem}{self.suffix_name}.{self.img_format}"
        return output_dir / output_file

    def inspect_image(self, image_path: PathLike | None = None) -> ImageProperties:
        if image_path is None:
            image_path = self.file
        try:
            with Image.open(image_path) as img:
                return ImageProperties(
                    filename=img.filename,
                    size=ImageSize(img.size[0], img.size[1]),
                    img_format=img.format,
                    mode=img.mode,
                )
        except UnidentifiedImageError as e:
            raise ValueError(f"File is not a valid image: {image_path}") from e

    def transform(
        self,
        size: tuple[int, int | Literal["auto"] | None],
        operation: Literal[
            "scale",
            "contain",
            "cover",
            "fit",
            "pad",
            "thumbnail",
        ] = "scale",
        **kwargs,
    ) -> None:
        """Transforms the image to the specified size and format.

        Args:
            size (tuple[int, int | Literal["auto"] | None]): The target size for the image.
            operation (Literal): The transformation operation to apply. Defaults to "scale". Options include:
                - "scale": Resizes image given a specific ratio (target width / source width).
                - "contain": Resizes image with max width/height within given size, maintaining aspect ratio.
                - "cover": Resizes image to fill the given size while maintaining aspect ratio, cropping if necessary.
                - "fit": Resized and cropped version, based on given size.
                - "pad": Resizes and pads the image, expanded to fill the requested aspect ratio and size.
        """

        width, height = size
        if height == "auto" or height is None:
            if operation not in ["scale", "thumbnail"]:
                raise ValueError("Height cannot be 'auto' or None for this operation.")
            with Image.open(self.file) as img:
                if img.mode not in ["RGB", "RGBA"]:
                    img = img.convert("RGB")
                ImageOps.scale(img, width / img.width).save(self._output(size[0]), **kwargs)

        else:
            self._process_image(self.file, size=(width, height), operation=operation, **kwargs)
        return None

    def _process_image(
        self,
        file_path: PathLike,
        size: tuple[int, int | Literal["auto"] | None],
        operation: Literal[
            "scale",
            "contain",
            "cover",
            "fit",
            "pad",
            "thumbnail",
        ] = "scale",
        **kwargs,
    ) -> None:
        with Image.open(file_path) as img:
            if img.mode not in ["RGB", "RGBA"]:
                img = img.convert("RGB")

            match operation:
                case "scale":
                    ImageOps.scale(img, size[0] / img.width).save(self._output(size[0]), **kwargs)
                case "contain":
                    ImageOps.contain(img, size).save(self._output(size[0]), **kwargs)
                case "cover":
                    ImageOps.cover(img, size).save(self._output(size[0]), **kwargs)
                case "fit":
                    ImageOps.fit(img, size).save(self._output(size[0]), **kwargs)
                case "pad":
                    ImageOps.pad(img, size).save(self._output(size[0]), **kwargs)
                case "thumbnail":
                    img.thumbnail(size)
                    img.save(self._output(size[0]), **kwargs)
                case _:
                    raise ValueError(f"Invalid operation: {operation}")
        return None

    def _output(self, width: int) -> Path:
        output_dir = Path(self.output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        output_file = f"{self.prefix_name}{Path(self.file).stem}{self.suffix_name}_{str(width)}.{self.img_format}"
        return output_dir / output_file
