from os import PathLike
from pathlib import Path
from typing import Literal

from attrs import define, field, validators

from webimage._scribe import HTMLWriter
from webimage._transformations import Mage
from webimage._typing import RenderSize
from webimage.properties import MediaCondition, ScaleSizes, Sizes, SrcsetItem


@define
class WebImage:
    """
    Responsible for rendering responsive images for the web.

    Attributes:
        source_path (PathLike): The path to the source image.
        destination_path (PathLike): The path to the destination directory where the rendered images will be saved.
        max_width (int): The maximum width of the rendered images in pixels. Default is 800.
        min_width (int): The minimum width of the rendered images in pixels. Default is 200.
        total_images (int): The total number of images to be rendered. Default is 3.
        img_format (str): The format of the rendered images (e.g., "jpg", "png"). Default is "webp".
        quality (int): The quality of the rendered images (1-100). Default is 80.
        optimize (bool): Whether to optimize the rendered images. Default is True.
        html_output (bool): Whether to generate an HTML snippet for the rendered images. Default is True.

        mage (Mage): An instance of the magical `Mage` class responsible for image transformations.

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

    mage: Mage | None = field(default=None, init=False)
    scribe: HTMLWriter | None = field(factory=HTMLWriter, init=False)

    def __attrs_post_init__(self):
        if not self.valid_filepath:
            raise ValueError(f"Invalid source path: {self.source_path}")

    @property
    def _is_dir(self) -> bool:
        return Path(self.source_path).is_dir()

    @property
    def _is_file(self) -> bool:
        return Path(self.source_path).is_file()

    @property
    def valid_filepath(self) -> bool:
        if not self._is_file and not self._is_dir:
            return False
        return True

    @property
    def breakpoints(self) -> list[int]:
        step = (self.max_width - self.min_width) // (self.total_images - 1)
        return [self.min_width + i * step for i in range(self.total_images)]

    def render(
        self,
        *,
        size: RenderSize | None = None,
        html_outer_tag: Literal["img", "picture", "figure"] = "img",
        html_prepend_path: str | None = "/static/",
        html_output_format: Literal["txt", "md", "html"] = "txt",
        **kwargs,
    ) -> None:
        """
        Renders the images according to the specified properties.

        Args:
            size (RenderSize): The size of the rendered images. Can be "small", "medium", "large", or "thumbnail".
            If None, the images will be rendered based on the breakpoints.
            html_outer_tag (Literal["img", "picture", "figure"]): The outermost HTML tag. Default is "img".
            html_prepend_path (str | None): The string that will be concatenated in front of the image name in the `img` and/or `srcset` HTML attributes.
            html_output_format (Literal["txt", "md", "html"]): The format of the HTML output file (e.g., "txt", "md", "html"). Default is "txt".
            kwargs: Additional keyword arguments for rendering, such as "prefix_name", "suffix_name", "breakpoints".
        """
        if size:
            # check if size_mapping in kwargs, if not use default mapping
            size_mapping = kwargs.get(
                "size_mapping",
                {
                    "small": ScaleSizes.SMALL,
                    "medium": ScaleSizes.MEDIUM,
                    "large": ScaleSizes.LARGE,
                    "thumbnail": ScaleSizes.THUMB,
                },
            )
            if size not in size_mapping:
                raise ValueError(f"Invalid render size: {size}. Must be one of {list(size_mapping.keys())}.")
            size = (size_mapping[size].width, size_mapping[size].height)

        if self._is_file:
            self._render_file(
                self.source_path,
                size=size,
                html_prepend_path=html_prepend_path,
                html_outer_tag=html_outer_tag,
                html_output_format=html_output_format,
                **kwargs,
            )
        elif self._is_dir:
            for file in Path(self.source_path).iterdir():
                if file.is_file():
                    try:
                        self._render_file(
                            file,
                            size=size,
                            html_prepend_path=html_prepend_path,
                            html_outer_tag=html_outer_tag,
                            html_output_format=html_output_format,
                            **kwargs,
                        )
                    except ValueError as e:
                        print(f"Error rendering {file}: {e}")
                        continue
        else:
            raise ValueError(f"Invalid source path: {self.source_path}")

    def _render_file(
        self,
        file_path: PathLike,
        size: tuple[int, int | Literal["auto"] | None] = None,
        html_prepend_path: str | None = None,
        html_outer_tag: Literal["img", "picture", "figure"] = "img",
        html_output_format: Literal["txt", "md", "html"] = "txt",
        **kwargs,
    ) -> None:
        """
        Renders a single image file.

        Args:
            file_path: The path to the image file to be rendered.
            size:
            kwargs: Additional keyword arguments.
        """
        self.mage = Mage(
            file=file_path,
            output_dir=self.destination_path or Path(file_path).parent,
            img_format=self.img_format,
            prefix_name=kwargs.get("prefix_name", ""),
            suffix_name=kwargs.get("suffix_name", ""),
        )

        if size:
            operation = "scale" if size[1] == "auto" else "fit"
            self.mage.transform(size=size, operation=operation, quality=self.quality, optimize=self.optimize)

            if self.html_output:
                NotImplementedError("HTML output for specific sizes is not yet implemented.")

            return None

        img_info = self.mage.inspect_image()
        max_img_px_width = min(img_info.size.width, self.max_width or 800)

        # List of image widths based on total_images and min/max widths
        breakpoints = kwargs.get("breakpoints", self.breakpoints)

        srcset_items = []
        for width in breakpoints:
            if width > max_img_px_width:
                continue

            self.mage.transform(size=(width, "auto"), quality=self.quality, optimize=self.optimize)

            if self.html_output:
                srcset_item = SrcsetItem(
                    prepend_path=html_prepend_path,
                    image_name=f"{Path(file_path).stem}_{str(width)}",
                    width=width,
                    img_format=self.img_format,
                )
                srcset_items.append(srcset_item)
                print(f"Rendered {srcset_item}")

        if not kwargs.get("media_conditions"):
            media_conditions = [
                MediaCondition(
                    min_or_max_width="max",
                    width_of_window=kwargs.get("viewport_min_width", 600),
                    image_width=kwargs.get("img_vw_width", 96),
                    image_unit="vw",
                )
            ]

        sizes = Sizes(
            media_conditions=media_conditions,
            default_width=kwargs.get("max_img_px_width", 1200),
            default_unit=kwargs.get("default_unit", "px"),
        )

        self.scribe.sizes = sizes
        self.scribe.srcset_items = srcset_items
        self.scribe.html_outer_tag = html_outer_tag

        self.scribe.write_to_file(
            f"{self.mage.output_dir}/{Path(file_path).stem}.{html_output_format}",
            css_class=kwargs.get("css_class", None),
        )

        return None
