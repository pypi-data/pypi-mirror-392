import logging

from bluepyll.core.bluepyll_element import BluePyllElement
from bluepyll.state_machine import BluestacksState
from bluepyll.controller.bluestacks_controller import BluestacksController
from bluepyll.controller.adb_controller import AdbController
from bluepyll.controller.image_controller import ImageController

logger = logging.getLogger(__name__)


class BluePyllController:
    def __init__(self, adb_host: str | None = None, adb_port: int | None = None):
        self.adb = AdbController(host=adb_host, port=adb_port)
        self.image = ImageController()
        self.bluestacks = BluestacksController(adb_controller=self.adb, image_controller=self.image)

    def disconnect(self) -> None:
        """Closes the ADB connection and performs cleanup."""
        if self.adb.is_connected():
            self.adb.disconnect()

    def click_coord(
        self,
        coords: tuple[int, int],
        times: int = 1,
    ) -> bool:
        # Ensure Bluestacks is ready before trying to click coords
        match self.bluestacks.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case BluestacksState.READY:
                is_connected = self.adb.is_connected()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'click_coords' method call."
                    )
                    return False
                tap_command: str = f"input tap {coords[0]} {coords[1]}"
                for _ in range(times - 1):
                    tap_command += f" && input tap {coords[0]} {coords[1]}"

                self.adb.shell_command(tap_command)
                logger.debug(
                    f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}"
                )
                return True

    def click_element(
        self,
        bluepyll_element: BluePyllElement,
        times: int = 1,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 2,
    ) -> bool:
        # Ensure Bluestacks is ready before trying to click ui
        match self.bluestacks.bluestacks_state.current_state:
            case BluestacksState.CLOSED | BluestacksState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case BluestacksState.READY:
                is_connected = self.adb.is_connected()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'click_element' method call."
                    )
                    return False
                coord: tuple[int, int] | None = self.image.where_element(
                    bs_controller=self.bluestacks,
                    bluepyll_element=bluepyll_element,
                    screenshot_img_bytes=screenshot_img_bytes,
                    max_retries=max_tries,
                )
                if not coord:
                    logger.debug(f"UI element {bluepyll_element.label} not found")
                    return False
                if self.click_coord(coord, times=times):
                    logger.debug(
                        f"Click event sent via ADB at coords x={coord[0]}, y={coord[1]}"
                    )
                    return True
                return False
            case _:
                logger.warning(
                    "Cannot click coords - BluePyllController.bluestacks_state.current_state is not in a valid state."
                    " Make sure it is in the 'BluestacksState.READY' state."
                )
                return False

    def click_elements(
        self,
        bluepyll_elements: list[BluePyllElement],
        screenshot_img_bytes: bytes = None,
        max_tries: int = 2,
    ) -> bool:
        return any(
            self.click_element(
                bluepyll_element=bluepyll_element,
                screenshot_img_bytes=screenshot_img_bytes,
                max_tries=max_tries,
            )
            for bluepyll_element in bluepyll_elements
        )
