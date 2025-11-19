from pathlib import Path


class BluePyllElement:
    """
    Represents a UI element.

    Attributes:
        label (str): Label of the element
        ele_type (str): Type of the element
        og_window_size (tuple[int, int]): The original size of the window the element was created from
        position (tuple[int, int] | None): Position of the element
        size (tuple[int, int] | None): Size of the element
        path (Path | None): Path to the element image
        is_static (bool): Whether the element is static or not
        confidence (float | None): Confidence of the element
        ele_txt (str | None): Text of the element
        pixel_color (tuple[int, int, int] | None): The color of the element(pixel) if 'ele_type' == 'pixel'
        region (tuple[int, int, int, int] | None): The region of the screenshot to look for the element
        center (tuple[int, int] | None): The coords of the center of the element
    """

    def __init__(
        self,
        label: str,
        ele_type: str,
        og_window_size: tuple[int, int],
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        path: Path | None = None,
        is_static: bool = True,
        confidence: float | None = None,
        ele_txt: str | None = None,
        pixel_color: tuple[int, int, int] | None = None,
    ) -> None:
        """
        Initialize a BluePyllElement.

        Args:
            label (str): Label of the element
            ele_type (str): Type of the element
            og_window_size (tuple[int, int]): The original size of the window the element was created from
            position (tuple[int, int] | None): Position of the element
            size (tuple[int, int] | None): Size of the element
            path (Path | None): Path to the element image
            is_static (bool): Whether the element is static or not
            confidence (float | None): Confidence of the element
            ele_txt (str | None): Text of the element
            pixel_color (tuple[int, int, int] | None): The color of the element(pixel) if 'ele_type' == 'pixel'
        """

        self.label: str = str(label).lower()
        self.ele_type: str = str(ele_type).lower()
        self.og_window_size: tuple[int, int] = int(og_window_size[0]), int(
            og_window_size[1]
        )
        self.position: tuple[int, int] | None = (
            (int(position[0]), int(position[1])) if position else None
        )
        self.size: tuple[int, int] | None = (
            (1, 1)
            if self.ele_type in ["pixel"]
            else (int(size[0]), int(size[1])) if size else None
        )
        self.path = None if self.ele_type in ["pixel"] else path
        self.is_static: bool = True if self.ele_type in ["pixel"] else is_static
        self.confidence: float | None = (
            None
            if self.ele_type in ["pixel", "text"]
            else float(confidence) if confidence else 0.7
        )
        self.ele_txt: str | None = (
            None if self.ele_type in ["pixel"] or not ele_txt else str(ele_txt).lower()
        )
        self.pixel_color: tuple[int, int, int] | None = (
            None
            if self.ele_type in ["button", "text", "input", "image"]
            else (
                (int(pixel_color[0]), int(pixel_color[1]), int(pixel_color[2]))
                if pixel_color
                else None
            )
        )
        self.region: tuple[int, int, int, int] | None = (
            None
            if self.ele_type in ["pixel"] or not self.position
            else (
                self.position[0],
                self.position[1],
                self.position[0] + self.size[0],
                self.position[1] + self.size[1],
            )
        )
        self.center: tuple[int, int] | None = (
            None
            if self.ele_type in ["text"]
            else (
                self.position
                if self.ele_type in ["pixel"]
                else (
                    (
                        self.position[0] + self.size[0] // 2,
                        self.position[1] + self.size[1] // 2,
                    )
                    if self.position and self.size
                    else None
                )
            )
        )

    def __repr__(self):
        return f"BluePyllElement(label={self.label}, ele_type={self.ele_type}, og_window_size={self.og_window_size}, position={self.position}, size={self.size}, path={self.path}, is_static={self.is_static}, confidence={self.confidence}, ele_txt={self.ele_txt}, pixel_color={self.pixel_color}, region={self.region}, center={self.center}, controller={self.controller})"
