import logging
import time

from adb_shell.adb_device import AdbDeviceTcp

from bluepyll.constants.adb_constants import AdbConstants
from bluepyll.core.bluepyll_app import BluePyllApp


class AdbController:
    """
    Handles device connection and all low-level ADB commands using adb-shell.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        timeout: int | None = None,
    ):
        self.host = host or AdbConstants.DEFAULT_IP
        self.port = port or AdbConstants.DEFAULT_PORT
        self.timeout = timeout or AdbConstants.DEFAULT_TIMEOUT
        self.device: AdbDeviceTcp | None = None

    def connect(self) -> bool:
        """Establishes the TCP connection to the ADB service."""
        self.logger.debug(f"Connecting to ADB at {self.host}:{self.port}...")

        match self.device:
            case None:
                self.logger.debug(
                    "ADB device not initialized. Attempting to initialize ADB device..."
                )
                self.device = AdbDeviceTcp(self.host, self.port)
        match self.device.available:
            case True:
                self.logger.debug("ADB device connected.")
                return True
            case False:
                self.logger.debug(
                    "ADB device not connected. Attempting to connect ADB device..."
                )

                try:
                    self.device.connect()
                    self.logger.debug("ADB connection successful.")
                    return True
                except Exception as e:
                    self.logger.warning(f"Error connecting to ADB: {e}")
                    self.device = None
                    return False

    def disconnect(self):
        self.logger.debug("Disconnecting ADB device...")
        match self.device:
            case None:
                self.logger.debug("ADB device not initialized.")
                return True
            case _:
                match self.device.available:
                    case True:
                        self.logger.debug(
                            "ADB device is connected. Attempting to disconnect ADB device..."
                        )
                        self.device.close()
                        match self.device.available:
                            case True:
                                self.logger.debug("ADB device not disconnected.")
                                return False
                            case False:
                                self.logger.debug("ADB device disconnected.")
                                return True

    def is_connected(self) -> bool:
        """Checks if the ADB device is connected."""
        match self.device:
            case None:
                self.logger.debug("ADB device not initialized.")
                return False
            case _:
                match self.device.available:
                    case True:
                        self.logger.debug("ADB device connected.")
                        return True
                    case False:
                        self.logger.debug("ADB device not connected.")
                        return False

    def shell_command(self, command: str):
        """Executes a shell command and returns the output."""
        self.logger.debug(f"Executing shell command: {command}")
        if not self.device:
            self.logger.warning("Error: ADB not connected.")
            return None

        return self.device.shell(
            command,
            timeout_s=self.timeout,
            read_timeout_s=self.timeout,
            transport_timeout_s=self.timeout,
            decode=False,
        )

    def tap(self, x, y):
        """Performs a simple tap at (x, y)."""
        self.logger.debug(f"Tapping at ({x}, {y})")
        self.shell_command(f"input tap {x} {y}")

    def open_app(
        self,
        app: BluePyllApp,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """
        Opens an app using the BluePyllApp object.

        Args:
            app: The BluePyllApp object to open
            timeout: The timeout for the ADB command
            wait_time: The wait time between retries

        Returns:
            bool: True if the app is opened, False otherwise
        """
        self.logger.debug(f"Opening app with package name: {app.package_name} ...")
        if not self.is_connected():
            self.logger.warning(
                "ADB device not initialized. Skipping 'open_app' method call."
            )
            return False
        # Wait for app to open by checking if it's running
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            self.shell_command(f"monkey -p {app.package_name} -v 1")
            match self.is_app_running(app, timeout=timeout, wait_time=wait_time):
                case True:
                    self.logger.debug(
                        f"App with package name: {app.package_name} opened via ADB"
                    )
                    return True
                case False:
                    time.sleep(wait_time)
                    continue
        # If app isn't running after timeout, raise error
        self.logger.warning(
            f"App with package name: {app.package_name} did not start within {timeout} seconds"
        )
        return False

    def is_app_running(
        self,
        app: BluePyllApp,
        timeout: int,
        wait_time: int,
        max_retries: int = 3,
    ) -> bool:
        """
        Check if an app is running.

        Args:
            app: The BluePyllApp object to check
            timeout: The timeout for the ADB command
            wait_time: The wait time between retries
            max_retries: The maximum number of retries to check if the app is running

        Returns:
            bool: True if the app is running, False otherwise
        """
        self.logger.debug(
            f"Checking if app with package name: {app.package_name} is running..."
        )
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'is_app_running' method call."
            )
            return False

        try:
            # Try multiple times to detect the app
            for i in range(max_retries):
                try:
                    # Get the list of running processes with a longer timeout
                    output: str = self.shell_command(
                        f"dumpsys window windows | grep -E 'mCurrentFocus' | grep {app.package_name}",
                    )
                except Exception as e:
                    self.logger.debug(f"Error checking app process: {e}")
                    time.sleep(wait_time)
                    continue
                if output:
                    self.logger.debug(f"Found app process: {output}")
                    return True
                else:
                    self.logger.debug(
                        f"{app.app_name.title()} app process not found. Retrying... {i + 1}/{max_retries}"
                    )
                    time.sleep(wait_time)
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Error checking if app is running: {e}")
            return False

    def close_app(
        self,
        app: BluePyllApp,
        timeout: int,
        wait_time: int,
    ) -> bool:
        self.logger.debug(f"Closing app with package name: {app.package_name}...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'close_app' method call."
            )
            return False

        start_time: float = time.time()
        while time.time() - start_time < timeout:
            self.shell_command(
                f"am force-stop {app.package_name}",
            )
            match self.is_app_running(app, timeout, wait_time):
                case True:
                    time.sleep(wait_time)
                    continue
                case False:
                    self.logger.debug(
                        f"App with package name: {app.package_name} closed via ADB"
                    )
                    return True
        # If app is still running after timeout
        self.logger.warning(
            f"App with package name: {app.package_name} did not close within {timeout} seconds"
        )
        return False

    def go_home(self) -> bool:
        self.logger.debug("Going to home screen...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'go_home' method call."
            )
            return False
        # Go to home screen
        self.shell_command("input keyevent 3")
        self.logger.debug("Home screen opened via ADB")
        return True

    def capture_screenshot(self) -> bytes | None:
        self.logger.debug("Capturing screenshot...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'capture_screenshot' method call."
            )
            return None
        try:
            # Capture the screenshot
            screenshot_bytes: bytes = self.shell_command("screencap -p")
            self.logger.debug("Screenshot captured successfully")
            return screenshot_bytes
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None

    def type_text(self, text: str) -> bool:
        self.logger.debug(f"Typing text: {text} ...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'type_text' method call."
            )
            return False
        # Send the text using ADB
        self.shell_command(f"input text {text}")
        self.logger.debug(f"Text '{text}' sent via ADB")
        return True

    def press_enter(self) -> bool:
        self.logger.debug("Pressing enter key...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'press_enter' method call."
            )
            return False
        # Send the enter key using ADB
        self.shell_command("input keyevent 66")
        self.logger.debug("Enter key sent via ADB")
        return True

    def press_esc(self) -> bool:
        self.logger.debug("Pressing esc key...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'press_esc' method call."
            )
            return False
        # Send the esc key using ADB
        self.shell_command("input keyevent 4")
        self.logger.debug("Esc key sent via ADB")
        return True

    def show_recent_apps(self) -> bool:
        """Show the recent apps drawer"""
        self.logger.debug("Showing recent apps...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'show_recent_apps' method call."
            )
            return False
        self.shell_command("input keyevent KEYCODE_APP_SWITCH")
        self.logger.debug("Recent apps drawer successfully opened")
        return True
