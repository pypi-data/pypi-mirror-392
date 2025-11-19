"""
Controller for managing the BlueStacks emulator.
"""

import io
import logging
import os
import time
from importlib.resources import files

import psutil
import win32con
import win32gui
from PIL import Image, ImageGrab

from bluepyll.core.bluepyll_element import BluePyllElement
from bluepyll.core.bluepyll_app import BluePyllApp
from bluepyll.state_machine import BluestacksState, StateMachine
from bluepyll.utils import validate_and_convert_int
from bluepyll.constants.bluestacks_constants import BluestacksConstants
from bluepyll.controller.image_controller import ImageController
from bluepyll.controller.adb_controller import AdbController

# Initialize logger
logger = logging.getLogger(__name__)


def log_property_setter(func):
    """
    Decorator to log property setter operations.

    Args:
        func: The property setter function to decorate

    Returns:
        The decorated function
    """

    def wrapper(self, value: object | None):
        logger.debug(f"Setting {func.__name__}...")
        result = func(self, value)
        logger.debug(f"{func.__name__} set to {value}")
        return result

    return wrapper


class BluestacksElements:
    """
    This class is used to store BlueStacks UI elements.
    """

    def __init__(self, controller):
        self.controller = controller

        self.bluestacks_loading_img: BluePyllElement = BluePyllElement(
            label="bluestacks_loading_img",
            ele_type="image",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_loading_img.png"),
            confidence=0.6,
            ele_txt="Starting BlueStacks",
        )

        self.bluestacks_my_games_button: BluePyllElement = BluePyllElement(
            label="bluestacks_my_games_buttoon",
            ele_type="button",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_my_games_buttoon.png"),
            confidence=0.6,
            ele_txt="My games",
        )

        self.bluestacks_store_search_input: BluePyllElement = BluePyllElement(
            label="bluestacks_store_search_input",
            ele_type="input",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_store_search_input.png"),
            is_static=False,
            confidence=0.6,
            ele_txt="Search for games & apps",
        )

        self.bluestacks_store_button: BluePyllElement = BluePyllElement(
            label="bluestacks_store_button",
            ele_type="button",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_store_button.png"),
            confidence=0.6,
        )

        self.bluestacks_playstore_search_inpput: BluePyllElement = BluePyllElement(
            label="bluestacks_playstore_search_input",
            ele_type="input",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath(
                "bluestacks_playstore_search_input.png"
            ),
            is_static=False,
            confidence=0.5,
            ele_txt="Search for games & apps",
        )

        # Loading elements
        self.bluestacks_loading_screen_img: BluePyllElement = BluePyllElement(
            label="bluestacks_loading_screen_img",
            ele_type="image",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("bluestacks_loading_screen_img.png"),
            is_static=False,
            confidence=0.99,
        )

        self.adb_screenshot_img: BluePyllElement = BluePyllElement(
            label="adb_screenshot_img",
            ele_type="image",
            og_window_size=self.controller.ref_window_size,
            path=files("bluepyll.assets").joinpath("adb_screenshot_img.png"),
            is_static=False,
            confidence=0.99,
        )


class BluestacksController:
    def __init__(self, adb_controller:AdbController, image_controller:ImageController) -> None:
        logger.info("Initializing BluestacksController")
        
        self._ref_window_size: tuple[int, int] = (
            BluestacksConstants.DEFAULT_REF_WINDOW_SIZE
        )
        self._filepath: str | None = None
        self._default_transport_timeout_s: int = 60.0
        self.running_apps: list[BluePyllApp] | list = list()
        self.bluestacks_state = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions(),
        )

        
        self.elements: BluestacksElements = BluestacksElements(self)
        self._autoset_filepath()

        self._adb_controller : AdbController = adb_controller
        self._image_controller : ImageController = image_controller

        self.bluestacks_state.register_handler(
            BluestacksState.LOADING, self.wait_for_load, None
        )
        self.bluestacks_state.register_handler(
            BluestacksState.READY, self._adb_controller.connect, None
        )

        self.open()
        logger.debug(
            f"BluestacksController initialized with the following state:\n{self.bluestacks_state}\n"
        )

    @property
    def ref_window_size(self) -> tuple[int, int] | None:
        return self._ref_window_size

    @ref_window_size.setter
    @log_property_setter
    def ref_window_size(self, width: int | str, height: int | str) -> None:
        if not isinstance(width, int):
            if isinstance(width, str) and width.isdigit():
                width: int = int(width)
                if width <= 0:
                    logger.warning(
                        "ValueError while trying to set BluestacksController 'ref_window_size': Provided width must be positive integers!"
                    )
                    raise ValueError("Provided width must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluestacksController 'ref_window_size': Provided width must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided width must be integer or the string representation of an integer!"
                )

        if not isinstance(height, int):
            if isinstance(height, str) and height.isdigit():
                height: int = int(height)
                if height <= 0:
                    logger.warning(
                        "ValueError while trying to set BluestacksController 'ref_window_size': Provided height must be positive integers!"
                    )
                    raise ValueError("Provided height must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluestacksController 'ref_window_size': Provided height must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided height must be integer or the string representation of an integer!"
                )

        self._ref_window_size = (width, height)

    @property
    def filepath(self) -> str | None:
        return self._filepath

    @filepath.setter
    @log_property_setter
    def filepath(self, filepath: str) -> None:
        """
        If the provided filepath is a string and it exist,
        sets the filepath to the BlueStacks Emulator.
        Otherwise, returns a ValueError
        """

        if not isinstance(filepath, str):
            logger.warning(
                "ValueError while trying to set BluestacksController 'filepath': Provided filepath must be a string!"
            )
            raise ValueError("Provided filepath must be a string")

        if not os.path.exists(filepath):
            logger.warning(
                "ValueError while trying to set BluestacksController 'filepath': Provided filepath does not exist!"
            )
            raise ValueError("Provided filepath does not exist")

        self._filepath: str = filepath

    def _autoset_filepath(self):
        logger.debug("Setting filepath...")

        # Common installation paths for BlueStacks
        search_paths = [
            # Standard Program Files locations
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks_nxt", "HD-Player.exe"
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "BlueStacks_nxt",
                "HD-Player.exe",
            ),
            # Alternative BlueStacks versions
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks", "HD-Player.exe"
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""), "BlueStacks", "HD-Player.exe"
            ),
            # Common custom installation paths
            "C:\\Program Files\\BlueStacks_nxt\\HD-Player.exe",
            "C:\\Program Files (x86)\\BlueStacks_nxt\\HD-Player.exe",
            "C:\\BlueStacks\\HD-Player.exe",
            "C:\\BlueStacks_nxt\\HD-Player.exe",
            # Check if file exists in current directory or subdirectories
            "HD-Player.exe",
        ]

        # Remove empty paths from environment variables
        search_paths = [
            path for path in search_paths if path and path != "HD-Player.exe"
        ]

        # Add current working directory relative paths
        cwd = os.getcwd()
        search_paths.extend(
            [
                os.path.join(cwd, "BlueStacks_nxt", "HD-Player.exe"),
                os.path.join(cwd, "BlueStacks", "HD-Player.exe"),
            ]
        )

        logger.debug(f"Searching for HD-Player.exe in {len(search_paths)} locations")

        for potential_path in search_paths:
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                self._filepath = potential_path
                logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                return
            else:
                logger.debug(f"Checked path (does not exist): {potential_path}")

        # If we still haven't found it, try a broader search
        logger.debug("Performing broader search for HD-Player.exe...")
        try:
            for root, dirs, files in os.walk("C:\\"):
                if "HD-Player.exe" in files:
                    potential_path = os.path.join(root, "HD-Player.exe")
                    if "bluestacks" in root.lower():
                        self._filepath = potential_path
                        logger.debug(
                            f"HD-Player.exe found via broad search: {self._filepath}"
                        )
                        return
        except Exception as e:
            logger.debug(f"Broad search failed: {e}")

        logger.error(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )
        logger.error(f"Searched paths: {search_paths}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"ProgramFiles: {os.environ.get('ProgramFiles')}")
        logger.error(f"ProgramFiles(x86): {os.environ.get('ProgramFiles(x86)')}")
        raise FileNotFoundError(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )

    def _capture_loading_screen(self) -> bytes | None:
        """Capture the loading screen of BlueStacks."""
        time.sleep(1.0)
        hwnd: int = win32gui.FindWindow(None, "Bluestacks App Player")
        if hwnd:
            try:
                # Restore the window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Pin the window to the foreground
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                )
                time.sleep(0.5)
                rect: tuple[int, int, int, int] = win32gui.GetWindowRect(hwnd)
                bluestacks_window_image: Image.Image = ImageGrab.grab(bbox=rect)
                time.sleep(0.5)

                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                bluestacks_window_image.save(img_byte_arr, format="PNG")
                img_byte_arr = img_byte_arr.getvalue()

                # Unpin the window from the foreground
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE
                )
                logger.debug("Loading screen captured as bytes")
                return img_byte_arr
            except Exception as e:
                logger.warning(f"Error capturing loading screen: {e}")
                raise Exception(f"Error capturing loading screen: {e}")
        else:
            logger.warning("Could not find 'Bluestacks App Player' window")
            return None

    def open(
        self,
        max_retries: int = BluestacksConstants.DEFAULT_MAX_RETRIES,
        wait_time: int = BluestacksConstants.DEFAULT_WAIT_TIME,
        timeout_s: int = BluestacksConstants.DEFAULT_TIMEOUT,
    ) -> None:
        max_retries: int = validate_and_convert_int(max_retries, "max_retries")
        wait_time: int = validate_and_convert_int(wait_time, "wait_time")
        timeout_s: int = validate_and_convert_int(timeout_s, "timeout_s")
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.info("Opening Bluestacks controller...")
                if not self._filepath:
                    self._autoset_filepath()
                try:
                    os.startfile(self._filepath)
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Failed to start Bluestacks: {e}")
                    raise ValueError(f"Failed to start Bluestacks: {e}")

                start_time: float = time.time()

                for attempt in range(max_retries):
                    is_open: bool = any(
                        p.name().lower() == "HD-Player.exe".lower()
                        for p in psutil.process_iter(["name"])
                    )
                    if is_open:
                        logger.info("Bluestacks controller opened successfully.")
                        self.bluestacks_state.transition_to(BluestacksState.LOADING)
                        return

                    if time.time() - start_time > timeout_s:
                        logger.error("Timeout waiting for Bluestacks window to appear")
                        raise Exception(
                            "Timeout waiting for Bluestacks window to appear"
                        )

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries}: Could not find Bluestacks window."
                    )
                    time.sleep(wait_time)

                logger.error(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
                raise Exception(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
            case BluestacksState.LOADING:
                logger.info(
                    "Bluestacks controller is already open and currently loading."
                )
                return
            case BluestacksState.READY:
                logger.info("Bluestacks controller is already open and ready.")
                return

    def is_loading(self) -> bool:
        """
        Checks if the emulator is currently loading by searching for the loading screen image.
        - If the emulator is loading(loading screen image is found):
            - If the 'BluestacksState' state is in the loading state:
                - The 'BluestacksState' state will stay in the loading state.
            - Otherwise:
                - The 'BluestacksState' state will transition to the loading state.
        - If the emulator is not loading(loading screen image is not found):
            - If the 'BluestacksState' state is in the closed state:
                - The 'BluestacksState' state will stay in the closed state.
            - If the 'BluestacksState' state is in the loading state:
                - The 'BluestacksState' state will transition to the ready state.
            - If the 'BluestacksState' state is in the ready state:
                - The 'BluestacksState' state will stay in the ready state.

        Returns:
            bool: Whether the emulator is loading.
        """

        loading_screen: tuple[int, int] | None = self._image_controller.where_element(
            bs_controller=self,
            bluepyll_element=self.elements.bluestacks_loading_img,
        )
        match isinstance(loading_screen, tuple):
            case True:
                match self.bluestacks_state.current_state:
                    case BluestacksState.LOADING:
                        logger.debug("Bluestacks is loading...")
                        return True
                    case _:
                        self.bluestacks_state.transition_to(BluestacksState.LOADING)
                        logger.debug("Bluestacks is loading...")
                        return True
            case False:
                match self.bluestacks_state.current_state:
                    case BluestacksState.CLOSED:
                        logger.debug("Bluestacks is closed")
                        return False
                    case BluestacksState.LOADING:
                        self.bluestacks_state.transition_to(BluestacksState.READY)
                        logger.debug("Bluestacks has finished loading")
                        return False
                    case BluestacksState.READY:
                        logger.debug("Bluestacks is ready")
                        return False

    def wait_for_load(self):
        logger.debug("Waiting for Bluestacks to load...")
        while self.bluestacks_state.current_state == BluestacksState.LOADING:
            if self.is_loading():
                logger.debug("Bluestacks is currently loading...")
                # Wait a bit before checking again
                time.sleep(BluestacksConstants.DEFAULT_WAIT_TIME)
            else:
                logger.debug("Bluestacks is not loading")
        logger.info("Bluestacks is loaded & ready.")

    def kill_bluestacks(self) -> bool:
        """
        Kill the Bluestacks controller process. This will also close the ADB connection.

        Returns:
            bool: True if Bluestacks was successfully killed, False otherwise
        """
        logger.info("Killing Bluestacks controller...")

        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.debug("Bluestacks is already closed.")
                return True
            case BluestacksState.LOADING | BluestacksState.READY:
                try:
                    for proc in psutil.process_iter(["pid", "name"]):
                        info = proc.info
                        if info["name"] == "HD-Player.exe":
                            proc.kill()
                            proc.wait(
                                timeout=BluestacksConstants.PROCESS_WAIT_TIMEOUT
                            )  # Wait for process to terminate
                            self.bluestacks_state.transition_to(BluestacksState.CLOSED)
                            logger.info("Bluestacks controller killed.")
                            return True
                    return False
                except Exception as e:
                    logger.error(f"Error in kill_bluestacks: {e}")
                    raise ValueError(f"Failed to kill Bluestacks: {e}")
