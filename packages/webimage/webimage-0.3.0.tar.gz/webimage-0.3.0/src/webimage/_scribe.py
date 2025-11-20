from os import PathLike
from textwrap import dedent
from typing import Literal

from attrs import define, field

from .properties import ImageProperties, Sizes, SrcsetItem


@define
class HTMLWriter:
    """
    Responsible for generating an HTML snippet for the rendered images.

    Attributes:
        srcset_items (list[SrcsetItem]): A list of `SrcsetItem` instances representing the items in the `srcset` attribute.
        sizes (Sizes): An instance of `Sizes` representing the `sizes` attribute.
        html_outer_tag (Literal["img", "picture", "figure"]): The outermost HTML tag. Default is "img".
    """

    srcset_items: list[SrcsetItem] | None = field(default=None)
    sizes: Sizes | None = field(default=None)
    html_outer_tag: Literal["img", "picture", "figure"] = field(default="img")

    def __str__(self) -> str:
        if self.html_outer_tag == "img":
            return self.create_srcset_snippet()
        elif self.html_outer_tag == "picture":
            raise NotImplementedError("The 'picture' tag is not yet implemented.")
        elif self.html_outer_tag == "figure":
            raise NotImplementedError("The 'figure' tag is not yet implemented.")
        else:
            raise ValueError(
                f"Invalid html_outer_tag: {self.html_outer_tag}. Must be one of 'img', 'picture', 'figure'."
            )

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

        Args:
            css_class (str): An optional CSS class to be added to the `img` tag. If None, no class will be added.
        """
        css_class = f'class="{css_class}"' if css_class else ""

        snippet = f"""
<img {css_class}
  srcset=
  "
{self._srcset_items_to_str()}
  "
  src="{self.srcset_items[-1].prepend_path}{self.srcset_items[-1].image_name}.{self.srcset_items[-1].img_format}"
  sizes="{str(self.sizes)}"
  alt="..."
/>
<!-- Remember to add alt text -->
"""

        print(f"Generated HTML snippet:\n{snippet.strip('s')}")
        return snippet

    def _srcset_items_to_str(self) -> str:
        """Takes a list of `_SrcsetItem` instances and returns a string representation for the `srcset` attribute.

        The string representation looks like this:
        ```
        /path/to/image1.webp 400w,
        /path/to/image2.webp 800w,
        /path/to/image3.webp 1200w
        ```
        It takes into account new lines for formatting purposes. It also removes the comma
        from the last item in the list.
        """
        return_str = ""
        for item in self.srcset_items:
            if item == self.srcset_items[-1]:
                return_str += f"\t{str(item)}"
            else:
                return_str += f"\t{str(item)},\n"
        return return_str

    def write_to_file(
        self,
        output_path: str,
        html_output_tag: Literal["img", "picture", "figure"] = "img",
        **kwargs,
    ) -> None:
        """Writes the generated HTML snippet to a file."""
        if html_output_tag not in ["img", "picture", "figure"]:
            raise ValueError(f"Invalid html_output_tag: {html_output_tag}. Must be one of 'img', 'picture', 'figure'.")
        if html_output_tag == "figure":
            raise NotImplementedError("The 'figure' tag is not yet implemented.")
        if html_output_tag == "picture":
            raise NotImplementedError("The 'picture' tag is not yet implemented.")
        with open(output_path, "w") as f:
            f.write(self.create_srcset_snippet(css_class=kwargs.get("css_class")))
