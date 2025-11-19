from __future__ import annotations

from typing import TYPE_CHECKING

from bluepyll.state_machine import AppLifecycleState, StateMachine

if TYPE_CHECKING:
    from bluepyll.controller.bluepyll_controller import BluePyllController
    from bluepyll.core.bluepyll_element import BluePyllElement
    from bluepyll.core.bluepyll_screen import BluePyllScreen


class BluePyllApp:
    def __init__(
        self,
        app_name: str,
        package_name: str,
        bluepyll_controller: BluePyllController | None = None,
        screens: dict[str, BluePyllScreen] | None = None,
    ) -> None:
        if not app_name:
            raise ValueError("app_name must be a non-empty string")
        if not package_name:
            raise ValueError("package_name must be a non-empty string")

        self.app_name: str = app_name
        self.package_name: str = package_name
        self.bluepyll_controller: BluePyllController | None = bluepyll_controller
        self.screens: dict[str, BluePyllScreen] = screens if screens is not None else {}

        self.app_state = StateMachine(
            current_state=AppLifecycleState.CLOSED,
            transitions=AppLifecycleState.get_transitions(),
        )

    def add_screen(self, screen: BluePyllScreen) -> None:
        self.screens[screen.name] = screen

    def open(self):
        if not self.bluepyll_controller:
            raise ValueError(
                f"{self.app_name}'s bluepyll_controller is not initialized"
            )
        self.bluepyll_controller.adb.open_app(self, timeout=60, wait_time=10)
        self.app_state.transition_to(AppLifecycleState.LOADING)

    def close(self):
        if not self.bluepyll_controller:
            raise ValueError(
                f"{self.app_name}'s bluepyll_controller is not initialized"
            )
        self.bluepyll_controller.adb.close_app(self, timeout=60, wait_time=10)
        self.app_state.transition_to(AppLifecycleState.CLOSED)

    def is_open(self) -> bool:
        return self.app_state.current_state == AppLifecycleState.OPEN

    def is_loading(self) -> bool:
        return self.app_state.current_state == AppLifecycleState.LOADING

    def is_closed(self) -> bool:
        return self.app_state.current_state == AppLifecycleState.CLOSED

    def is_element_visible(self, bluepyll_element: BluePyllElement) -> bool:
        if not self.bluepyll_controller:
            raise ValueError(
                f"{self.app_name}'s bluepyll_controller is not initialized"
            )
        return (
            self.bluepyll_controller.image.where_element(
                bs_controller=self.bluepyll_controller.bluestacks,
                bluepyll_element=bluepyll_element,
            )
            is not None
        )
