# BluePyll: BlueStacks Automation Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![PyPI Version](https://img.shields.io/badge/pypi-0.1.13-blue.svg)](https://pypi.org/project/bluepyll)
[![Documentation](https://img.shields.io/badge/docs-readthedocs.io-green.svg)](https://bluepyll.readthedocs.io)

> Automate the BlueStacks Android emulator with structured state machines, ADB control, and template-driven UI interactions.

BluePyll targets Windows users who need reliable, scriptable control of Android apps running inside BlueStacks. The framework combines a robust controller stack (BlueStacks lifecycle management, ADB over TCP, and PIL/pyautogui-based vision) with a declarative way to describe screens and UI elements.

⚠️ **Disclaimer**: UI automation can violate application ToS. Use responsibly.

## 📋 Table of Contents

- [✨ Features](#-features)
- [📦 Prerequisites](#-prerequisites)
- [🚀 Installation](#-installation)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [⚡ Quick Start](#-quick-start)
- [🛠 Building UI Automation](#-building-ui-automation)
- [🔍 Working with Controllers](#-working-with-controllers)
- [🧠 State Machines & Handlers](#-state-machines--handlers)
- [⚙️ Configuration Reference](#️-configuration-reference)
- [🧪 Troubleshooting & Diagnostics](#-troubleshooting--diagnostics)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

### Emulator & Lifecycle Control

- Auto-discovers and launches `HD-Player.exe`, pinning the window when needed.
- Tracks BlueStacks readiness via a finite-state machine and image-based loading detection.
- Provides cleanup helpers (kill emulator, disconnect ADB) for graceful shutdown.

### Application Automation

- `BluePyllApp` models Android packages, owns their lifecycle FSM, and uses the shared controller to open/close apps.
- Screens and elements are declarative Python objects; they live alongside your project assets.
- Hooks allow you to wait for custom conditions (loading screens, login gates, etc.).

### UI Interaction

- Template matching powered by `pyautogui.locate` with automatic scaling to current emulator resolution.
- Pixel-color and OCR checks via OpenCV + EasyOCR for scenarios where images are not ideal.
- Coordinate tapping, repeated clicks, text entry, navigation keys, and more forwarded over ADB.

### System Integrations

- Uses `adb-shell` for TCP connections to the BlueStacks instance.
- Exposes raw ADB shell access for advanced commands.
- Ships a curated set of reference UI elements for the emulator shell itself (My Games, Store search, loading screen, etc.).

## 📦 Prerequisites

- **Windows 10/11** (x64, administrator privileges recommended).
- **BlueStacks 5+** installed locally (default paths preferred for auto-discovery).
- **Python 3.13+** (matching the versions declared in `pyproject.toml`).
- **uv** for dependency management ([installation guide](https://docs.astral.sh/uv/getting-started/installation)).

## 🚀 Installation

```bash
# 1. Ensure uv is installed once per machine.
# 2. Inside your project root:
uv add bluepyll
```

From source:

```bash
git clone https://github.com/IAmNo1Special/BluePyll.git
cd BluePyll
uv sync  # installs runtime + dev dependencies defined in pyproject.toml / uv.lock
```

> 💡 All development and CI commands in this project are expressed through `uv` (e.g., `uv run pytest`).

## 🏗️ Architecture Overview

| Layer | Modules | Responsibilities |
| --- | --- | --- |
| **Controllers** | `controller/adb_controller.py`, `controller/image_controller.py`, `controller/bluestacks_controller.py`, `controller/bluepyll_controller.py` | Manage ADB TCP sessions, template matching, BlueStacks lifecycle, and aggregate helpers (`BluePyllController`). |
| **Core models** | `core/bluepyll_element.py`, `core/bluepyll_screen.py`, `core/bluepyll_app.py` | Describe UI elements, group them into screens, and model an app’s lifecycle + state machine. |
| **State & constants** | `state_machine.py`, `constants/adb_constants.py`, `constants/bluestacks_constants.py` | Reusable finite-state machine implementation plus shared timeout/window-size defaults. |
| **Utilities** | `utils.py`, `exceptions.py` | OCR helpers (`ImageTextChecker`), validation utilities, and domain-specific exception types. |

The package root re-exports these pieces for ergonomic imports (`from bluepyll import BluePyllController, BluePyllApp, ...`).

## ⚡ Quick Start

```python
from bluepyll import BluePyllController, BluePyllApp, AppLifecycleState

# Launches BlueStacks and primes ADB/image helpers.
controller = BluePyllController(adb_host="127.0.0.1", adb_port=5555)

# Model your target app. Attach the shared controller so lifecycle helpers can use it.
revomon = BluePyllApp(
    app_name="revomon",
    package_name="com.revomon.vr",
    bluepyll_controller=controller,
)

revomon.open()  # uses controller.adb to launch the Android package

if revomon.is_loading():
    print("Waiting for loading screen to clear...")

# ...interact via controller.click_coord / click_element / controller.adb.shell_command

revomon.close()
controller.disconnect()  # optional cleanup
```

## 🛠 Building UI Automation

BluePyll encourages you to codify UI knowledge using elements → screens → apps.

```python
from pathlib import Path
from time import sleep

from bluepyll import (
    BluePyllController,
    BluePyllApp,
    BluePyllScreen,
    BluePyllElement,
    AppLifecycleState,
)


class StartGameButton(BluePyllElement):
    def __init__(self):
        super().__init__(
            label="start_game_button",
            ele_type="button",
            og_window_size=(1920, 1080),
            path=str(Path(__file__).parent / "assets" / "start_game_button.png"),
            position=(740, 592),
            size=(440, 160),
            confidence=0.7,
            ele_txt="start game",
        )


class StartGameScreen(BluePyllScreen):
    def __init__(self):
        super().__init__(name="start_game", elements={"start": StartGameButton()})


class RevomonApp(BluePyllApp):
    def __init__(self, controller: BluePyllController):
        super().__init__(
            app_name="revomon",
            package_name="com.revomon.vr",
            bluepyll_controller=controller,
            screens={"start": StartGameScreen()},
        )
        self.app_state.register_handler(
            AppLifecycleState.LOADING,
            self.wait_for_start_button,
        )

    def wait_for_start_button(self) -> None:
        start_btn = self.screens["start"].elements["start"]
        while not self.is_element_visible(start_btn):
            sleep(1)
        self.app_state.transition_to(AppLifecycleState.READY)

    def click_start(self) -> None:
        self.bluepyll_controller.click_element(
            self.screens["start"].elements["start"]
        )


controller = BluePyllController()
revomon = RevomonApp(controller)
revomon.open()
revomon.click_start()
```

Key ideas:

1. **Elements** capture how to find something (image path, expected size, optional pixel color, OCR text, etc.).
2. **Screens** namespace related elements for readability.
3. **Apps** own lifecycle logic, state handlers, and call back into the shared controller for actions.

## 🔍 Working with Controllers

`BluePyllController` is the primary façade. It exposes three tuned subsystems:

1. `controller.adb` (`AdbController`) – connect/disconnect, `shell_command`, `type_text`, `press_enter`, `capture_screenshot`, `open_app`, etc.
2. `controller.image` (`ImageController`) – `where_element`, `where_elements`, `check_pixel_color`, OCR assistance through `ImageTextChecker`.
3. `controller.bluestacks` (`BluestacksController`) – emulator state machine, predefined `BluestacksElements`, window capture utilities, and lifecycle helpers (`open`, `kill_bluestacks`, `is_loading`).

Typical interactions:

```python
controller.click_coord((400, 900), times=2)
controller.click_element(my_element, max_tries=3)

# Direct ADB shell access
controller.adb.shell_command("input keyevent 3")  # Home
controller.adb.type_text("hello world")

# Vision helpers
coord = controller.image.where_element(
    bs_controller=controller.bluestacks,
    bluepyll_element=my_element,
)

# Emulator lifecycle
controller.bluestacks.wait_for_load()
controller.bluestacks.kill_bluestacks()
```

## 🧠 State Machines & Handlers

- `BluestacksState` transitions: `CLOSED → LOADING → READY` with automatic handlers registered inside `BluestacksController` (connect ADB when ready, poll loading screens while booting).
- `AppLifecycleState`: `CLOSED → LOADING → READY`. Each `BluePyllApp` owns a `StateMachine` so you can register custom `on_enter`/`on_exit` hooks (loading waits, login gating, etc.).
- The generic `StateMachine` (`state_machine.py`) validates transitions and runs handlers atomically, so your app logic stays predictable.

## ⚙️ Configuration Reference

| Constant | Default | Description |
| --- | --- | --- |
| `BluestacksConstants.DEFAULT_REF_WINDOW_SIZE` | `(1920, 1080)` | Reference resolution for scaling template images. |
| `BluestacksConstants.DEFAULT_MAX_RETRIES` | `10` | Attempts when polling emulator launch or vision tasks. |
| `BluestacksConstants.DEFAULT_TIMEOUT` | `30` seconds | Timeout for emulator boot helpers. |
| `AdbConstants.DEFAULT_PORT` | `5555` | TCP port used by BlueStacks ADB bridge. |
| `AdbConstants.APP_START_TIMEOUT` | `60` seconds | Cap for waiting on an Android process to appear. |

Override them in your code (pass constructor arguments, mutate constants, or extend the controllers) when your environment differs.

## 🧪 Troubleshooting & Diagnostics

| Symptom | Checks |
| --- | --- |
| **"Could not find HD-Player.exe"** | Ensure BlueStacks is installed, or call `controller.bluestacks.filepath = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"`. The auto-discovery walks common Program Files + `C:\` if needed. |
| **ADB connection fails** | Confirm BlueStacks is running and listening on `127.0.0.1:5555`, verify no firewall is blocking TCP, and rerun `controller.adb.connect()`. |
| **Element not found** | Match the source resolution in `BluePyllElement.og_window_size`, lower/raise `confidence`, or provide `region`/`position` hints to shrink the search box. |
| **OCR misreads** | Supply higher-resolution assets or rely on pixel/color detection via `ImageController.check_pixel_color`. |

Enable verbose logging while debugging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome issues, PRs, and new element definitions.

```bash
git clone https://github.com/IAmNo1Special/BluePyll.git
cd BluePyll

uv sync --dev      # install project + dev deps
uv run pytest      # run test suite
uv run ruff check  # style/lint (if configured)
```

1. Create a topic branch (`git switch -c feature/my-feature`).
2. Make focused commits with tests/docs.
3. Run the checks above.
4. Open a PR with context + screenshots/logs if UI-related.

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE).

## 🙏 Acknowledgments

- **BlueStacks** – Android emulator shell.
- **PyAutoGUI & Pillow** – image capture and template matching.
- **EasyOCR & OpenCV** – text extraction utilities.
- **adb-shell** – reliable TCP driver for ADB.

## 📞 Support

- Documentation: [bluepyll.readthedocs.io](https://bluepyll.readthedocs.io)
- Issues: [GitHub Issues](https://github.com/IAmNo1Special/BluePyll/issues)
- Discussions: [GitHub Discussions](https://github.com/IAmNo1Special/BluePyll/discussions)

> Built with ❤️ for automation enthusiasts — consider starring the repo if BluePyll saves you time!
