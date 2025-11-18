from os import PathLike
from textwrap import dedent

from attrs import define

from ._properties import ImageProperties, Sizes, SrcsetItem


@define
class HTMLWriter:
    """
    Responsible for generating an HTML snippet for the rendered images.

    Attributes:
        srcset_items: A list of `_SrcsetItem` instances representing the items in the `srcset` attribute.
        sizes: An instance of `_Sizes` representing the `sizes` attribute.
        img_format: The format of the rendered images (e.g., "webp", "jpg", "png").
    """

    srcset_items: list[SrcsetItem]
    sizes: Sizes
    img_format: str = "webp"

    def __str__(self) -> str:
        return self.create_srcset_snippet()

    def create_srcset_snippet(
        self,
        css_class: str | None = None,
    ) -> str:
        """Creates html block for responsive images.

        The output looks like this:
        ```
        <img
          srcset=
          "
            /path/to/image1.webp 400w,
            /path/to/image2.webp 800w,
            /path/to/image3.webp 1200w
          "
          src="/path/to/image3.webp"
          sizes="(max-width: 800px) 100vw, 1200px"
          alt="..."
        />
        <!-- Remember to add alt text -->
        ```
        """
        css_class = f'class="{css_class}"' if css_class else ""

        snippet = f"""
<img {css_class}
  srcset=
  "
{self._srcset_items_to_str()}
  "
  src="{self.srcset_items[-1].prepend_path}{self.srcset_items[-1].image_name}.{self.img_format}"
  sizes="{self._sizes_to_str()}"
  alt="..."
/>
<!-- Remember to add alt text -->
"""

        print(f"Generated HTML snippet:\n{snippet.strip('s')}")
        return snippet

    def _srcset_items_to_str(self) -> str:
        """Takes a list of `_SrcsetItem` instances and returns a string representation for the `srcset` attribute.

        The string representanion looks like this:
        ```
        '/path/to/image1.webp 400w,
        /path/to/image2.webp 800w,
        /path/to/image3.webp 1200w'
        ```
        It takes into account new lines for formatting purposes. It also removes the comma
        from the last item in the list.
        """
        return_str = ""
        for item in self.srcset_items:
            if item == self.srcset_items[-1]:
                return_str += str(item)
            else:
                return_str += f"{str(item)},\n"
        return return_str

    def _sizes_to_str(self) -> str:
        """Takes an instance of `_Sizes` and returns a string representation for the `sizes` attribute.

        The string representanion looks like this:
        ```
        "(max-width: 800px) 100vw, 1200px"
        ```
        """
        return f"(max-width: {self.sizes.max_viewport_width}px) {self.sizes.img_vw_width}vw, {self.sizes.max_img_px_width}px"

    def write_to_file(self, output_path: str, **kwargs) -> None:
        """Writes the generated HTML snippet to a file."""
        with open(output_path, "w") as f:
            f.write(self.create_srcset_snippet(css_class=kwargs.get("css_class")))
