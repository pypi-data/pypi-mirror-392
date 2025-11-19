import logging
from io import BytesIO
from time import sleep


from adb_shell.exceptions import TcpTimeoutException
from PIL import Image
from pyautogui import ImageNotFoundException, center, locate

from bluepyll.constants.bluestacks_constants import BluestacksConstants
from bluepyll.core.bluepyll_element import BluePyllElement
from bluepyll.state_machine import BluestacksState
from bluepyll.utils import ImageTextChecker

logger = logging.getLogger(__name__)


class ImageController:
    def __init__(self):
        self.img_txt_checker: ImageTextChecker = ImageTextChecker()

    def scale_img_to_screen(
        self,
        image_path: str,
        screen_image: str | Image.Image | bytes,
        og_window_size: tuple[int, int],
    ) -> Image.Image:
        # If screen_image is bytes, convert to PIL Image
        if isinstance(screen_image, bytes):
            screen_image = Image.open(BytesIO(screen_image))

        # If screen_image is a string (file path), open it
        elif isinstance(screen_image, str):
            screen_image = Image.open(screen_image)

        # At this point, screen_image should be a PIL Image
        game_screen_width, game_screen_height = screen_image.size

        needle_img: Image.Image = Image.open(image_path)

        needle_img_size: tuple[int, int] = needle_img.size

        original_window_size: tuple[int, int] = og_window_size

        ratio_width: float = game_screen_width / original_window_size[0]
        ratio_height: float = game_screen_height / original_window_size[1]

        scaled_image_size: tuple[int, int] = (
            int(needle_img_size[0] * ratio_width),
            int(needle_img_size[1] * ratio_height),
        )
        scaled_image: Image.Image = needle_img.resize(scaled_image_size)
        return scaled_image

    def check_pixel_color(
        self,
        target_coords: tuple[int, int],
        target_color: tuple[int, int, int],
        image: bytes | str,
        tolerance: int = 0,
    ) -> bool:
        """Check if the pixel at (x, y) in the given image matches the target color within a tolerance."""

        def check_color_with_tolerance(
            color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int
        ) -> bool:
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

        try:
            if len(target_coords) != 2:
                raise ValueError("Coords must be a tuple of two values")
            if len(target_color) != 3:
                raise ValueError("Target color must be a tuple of three values")
            if tolerance < 0:
                raise ValueError("Tolerance must be a non-negative integer")

            if not image:
                raise ValueError("Failed to capture screenshot")

            if isinstance(image, bytes):
                with Image.open(BytesIO(image)) as image:
                    pixel_color = image.getpixel(target_coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            elif isinstance(image, str):
                with Image.open(image) as image:
                    pixel_color = image.getpixel(target_coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            else:
                raise ValueError("Image must be a bytes or str")

        except ValueError as e:
            logger.error(f"ValueError in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")
        except Exception as e:
            logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")

    def where_element(
        self,
        bs_controller,
        bluepyll_element: BluePyllElement,
        screenshot_img_bytes: bytes = None,
        max_retries: int = 2,
    ) -> tuple[int, int] | None:
        # Ensure Bluestacks is loading or ready before trying to find UI element
        if not bluepyll_element.path:
            logger.warning("Cannot find UI element - BluePyllElement path is not set")
            return None
        match bs_controller.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.warning("Cannot find UI element - Bluestacks is closed")
                return None
            case BluestacksState.LOADING | BluestacksState.READY:
                logger.debug(f"Finding UI element. Max retries: {max_retries}")
                logger.debug(
                    f"Looking for BluePyllElement: {bluepyll_element.label} with confidence of {bluepyll_element.confidence}..."
                )
                find_ui_retries: int = 0
                while (
                    (find_ui_retries < max_retries)
                    if max_retries is not None and max_retries > 0
                    else True
                ):
                    try:
                        screen_image: bytes | None = (
                            screenshot_img_bytes
                            if screenshot_img_bytes
                            else (
                                bs_controller._capture_loading_screen()
                                if bluepyll_element.path
                                == bs_controller.elements.bluestacks_loading_img.path
                                else bs_controller._adb_controller.capture_screenshot()
                            )
                        )
                        if screen_image:
                            haystack_img: Image.Image = Image.open(
                                BytesIO(screen_image)
                            )
                            scaled_img: Image.Image = self.scale_img_to_screen(
                                image_path=bluepyll_element.path,
                                screen_image=haystack_img,
                                og_window_size=bs_controller.ref_window_size,
                            )
                            ui_location: tuple[int, int, int, int] | None = locate(
                                needleImage=scaled_img,
                                haystackImage=haystack_img,
                                confidence=bluepyll_element.confidence,
                                grayscale=True,
                                region=bluepyll_element.region,
                            )
                            if ui_location:
                                logger.debug(
                                    f"BluePyllElement {bluepyll_element.label} found at: {ui_location}"
                                )
                                ui_x_coord, ui_y_coord = center(ui_location)
                                return (ui_x_coord, ui_y_coord)
                    except ImageNotFoundException or TcpTimeoutException:
                        find_ui_retries += 1
                        logger.debug(
                            f"BluePyllElement {bluepyll_element.label} not found. Retrying... ({find_ui_retries}/{max_retries})"
                        )
                        sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
                        continue

                logger.debug(
                    f"Wasn't able to find BluePyllElement: {bluepyll_element.label}"
                )
                return None

    def where_elements(
        self,
        bs_controller,
        ui_elements: list[BluePyllElement],
        screenshot_img_bytes: bytes = None,
        max_tries: int = 2,
    ) -> tuple[int, int] | None:
        coord: tuple[int, int] | None = None
        for ui_element in ui_elements:
            coord = self.where_element(
                bs_controller=bs_controller,
                bluepyll_element=ui_element,
                screenshot_img_bytes=screenshot_img_bytes,
                max_retries=max_tries,
            )
            if coord:
                return coord
        return None
