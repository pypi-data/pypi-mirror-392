"""
Constants for ADB configuration
"""


class AdbConstants:
    """
    Constants for ADB configuration.

    These constants define default values and timeouts for the ADB service.
    """

    # Network configuration
    DEFAULT_IP: str = "127.0.0.1"
    DEFAULT_PORT: int = 5555

    # Operation timeouts
    DEFAULT_MAX_RETRIES: int = 10
    DEFAULT_WAIT_TIME: int = 1
    DEFAULT_TIMEOUT: int = 30
    PROCESS_WAIT_TIMEOUT: int = 10
    APP_START_TIMEOUT: int = 60
