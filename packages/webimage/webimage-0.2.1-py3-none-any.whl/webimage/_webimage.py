from os import PathLike
from pathlib import Path
from textwrap import dedent
from typing import Literal

from attrs import define, field, validators

from webimage._properties import ImageProperties, Sizes, SrcsetItem
from webimage._scribe import HTMLWriter
from webimage._transformations import Mage
from webimage._typing import ImageWidth, RenderSize


@define
class WebImage:
    """
    Responsible for rendering responsive images for the web.

    Attributes:
        source_path: The path to the source image.
        destination_path: The path to the destination directory where the rendered images will be saved.
        max_width: The maximum width of the rendered images in pixels.
        min_width: The minimum width of the rendered images in pixels.
        total_images: The total number of images to be rendered.
        img_format: The format of the rendered images (e.g., "jpg", "png").
        quality: The quality of the rendered images (1-100).
        html_output: Whether to generate an HTML snippet for the rendered images.
        html_srcset_path: The string that will be concatenated in front of the image name in the `srcset` attribute.
        mage: An instance of the magical `Mage` class responsible for image transformations.

    """

    source_path: PathLike
    destination_path: PathLike = field(default=None, kw_only=True)
    max_width: int = field(default=800, kw_only=True)
    min_width: int = field(default=200, kw_only=True)
    total_images: int = field(default=3, kw_only=True, validator=validators.optional(validators.in_(range(1, 6))))
    img_format: str = field(default="webp", kw_only=True)
    quality: int = field(default=80, kw_only=True, validator=validators.in_(range(1, 101)))
    optimize: bool = field(default=True, kw_only=True)
    html_output: bool = field(default=True, kw_only=True)
    html_srcset_path: str | None = field(default=None, kw_only=True)

    mage: Mage | None = field(default=None, init=False)

    @property
    def _is_dir(self) -> bool:
        return Path(self.source_path).is_dir()

    @property
    def _is_file(self) -> bool:
        return Path(self.source_path).is_file()

    @property
    def file_is_valid(self) -> bool:
        if not self._is_file and not self._is_dir:
            return False
        return True

    def render(self, *, size: RenderSize | None = None, **kwargs) -> None:
        """
        Renders the images according to the specified properties.
        """
        if self._is_file:
            self._render_file(self.source_path, size=size, **kwargs)
        elif self._is_dir:
            for file in Path(self.source_path).iterdir():
                if file.is_file():
                    try:
                        self._render_file(file, size=size, **kwargs)
                    except ValueError as e:
                        print(f"Error rendering {file}: {e}")
                        continue
        else:
            raise ValueError(f"Invalid source path: {self.source_path}")

    def _render_file(self, file_path: PathLike, size: RenderSize | None = None, **kwargs) -> None:
        """
        Renders a single image file.

        Args:
            file_path: The path to the image file to be rendered.
        """
        self.mage = Mage(
            file=file_path,
            output_dir=self.destination_path or Path(file_path).parent,
            img_format=self.img_format,
            prefix_name=kwargs.get("prefix_name", ""),
            suffix_name=kwargs.get("suffix_name", ""),
        )
        if not size:
            img_info = self.mage.inspect_image()
            max_img_px_width = min(img_info.size.width, self.max_width or 800)

            # List of widths based on total_images and min/max widths
            breakpoints = kwargs.get("breakpoints", self.breakpoints)

            srcset_items = []
            for width in breakpoints:
                if width > max_img_px_width:
                    continue

                self.mage.transform(size=(width, "auto"), quality=self.quality, optimize=self.optimize)

                srcset_item = SrcsetItem(
                    prepend_path=self.html_srcset_path or "/static/",
                    image_name=f"{Path(file_path).stem}_{str(width)}",
                    width=width,
                    img_format=self.img_format,
                )
                srcset_items.append(srcset_item)
                print(f"Rendered {srcset_item}")

                sizes = Sizes(
                    max_viewport_width=kwargs.get("viewport_max_width", max_img_px_width),
                    img_vw_width=kwargs.get("img_vw_width", 96),
                    max_img_px_width=max_img_px_width,
                )

            if self.html_output:
                html_writer = HTMLWriter(
                    srcset_items=srcset_items,
                    sizes=sizes,
                    img_format=self.img_format,
                )

                html_writer.write_to_file(f"{self.mage.output_dir}/{Path(file_path).stem}.txt", **kwargs)

        else:
            if size == "small":
                width = 350
                height = "auto"
            elif size == "medium":
                width = 600
                height = "auto"
            elif size == "large":
                width = 1200
                height = "auto"
            elif size == "thumbnail":
                width = 150
                height = 150
            else:
                raise ValueError(f"Invalid render size: {size}")

            self.mage.transform(size=(width, height), quality=self.quality, optimize=self.optimize)

            return None

        return None

    @property
    def breakpoints(self) -> list[int]:
        step = (self.max_width - self.min_width) // (self.total_images - 1)
        return [self.min_width + i * step for i in range(self.total_images)]
