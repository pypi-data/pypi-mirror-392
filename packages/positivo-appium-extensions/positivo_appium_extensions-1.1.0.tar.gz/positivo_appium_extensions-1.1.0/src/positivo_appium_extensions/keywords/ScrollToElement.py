"""
Scroll To Element

Scrolls the mobile screen or a container element until the specified target element becomes visible.
Uses swipe gestures internally through Appium.

This keyword repeatedly performs swipe gestures in the specified direction until the target element
is located or the maximum number of swipes is reached.

The keyword allows control of swipe direction, distance, duration, and number of attempts.
It can also restrict scrolling inside a specific container element.

Example:
    | Scroll To Element | id=login-button | max_swipes=7 | direction=down | swipe_distance_ratio=0.4 | duration=500 |
    | Scroll To Element | xpath=//android.widget.TextView[@text="Settings"] | direction=up | max_swipes=5 |
    | Scroll To Element | accessibility_id=NextButton | direction=right | container_locator=id=listContainer |

[Arguments]
    | locator              | (string) Locator of the target element to be found. Required. |
    | max_swipes           | (integer) Maximum number of swipes before failing. Default is 5. |
    | direction            | (string) Scroll direction: "down", "up", "left", or "right". Default is "down". |
    | swipe_distance_ratio | (float) Fraction of screen or container size for each swipe. Valid range: 0.1–0.99. Default is 0.4. |
    | duration             | (integer) Duration of each swipe in milliseconds. Default is 500. |
    | container_locator    | (string) Locator of the container element where scrolling is performed. Optional. |

[Return Values]
    None. The keyword stops when the target element becomes visible or raises an exception if it cannot be found.

[Raises]
    | ValueError   | If invalid parameters are provided (e.g., invalid direction or ratio). |
    | RuntimeError | If the target element is not found after the maximum number of swipes. |

Notes:
    - The keyword stops as soon as the target element becomes visible.
    - If a container locator is provided, scrolling occurs only inside that element.
    - Uses the Appium "mobile: swipeGesture" command internally.
"""
import random
import time
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.mouse_button import MouseButton


class ScrollToElement:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self._builtin = BuiltIn()

    @property
    def driver(self):
        return self._builtin.get_library_instance("AppiumLibrary")._current_application()

    def _adjust_to_screen_bounds(self, x, y, screen_width, screen_height):
        return max(0, min(x, screen_width)), max(0, min(y, screen_height))

    def _is_element_visible(self, locator):
        try:
            appium_lib = self._builtin.get_library_instance("AppiumLibrary")
            element = appium_lib._element_find(locator, True, True)
            return element.is_displayed()
        except:
            return False

    def _get_element_area_center(self, locator):
        appium_lib = self._builtin.get_library_instance("AppiumLibrary")
        element = appium_lib._element_find(locator, True, True)
        if not element:
            raise RuntimeError(f"Element not found for locator: {locator}")
        location = element.location
        size = element.size
        x, y = location["x"], location["y"]
        width, height = size["width"], size["height"]
        center_x = x + width / 2
        center_y = y + height / 2
        return x, y, width, height, center_x, center_y

    def _perform_scroll(self, start_x, start_y, end_x, end_y, duration=500, steps=20):
        driver = self.driver
        actions = ActionChains(driver)
        actions.w3c_actions.devices = []
        finger = actions.w3c_actions.add_pointer_input("touch", "finger1")

        finger.create_pointer_move(x=start_x, y=start_y)
        finger.create_pointer_down(button=MouseButton.LEFT)
        finger.create_pause(0.05)

        for i in range(1, steps + 1):
            t = i / steps
            interp_x = start_x + t * (end_x - start_x) + random.uniform(-0, 0)
            interp_y = start_y + t * (end_y - start_y) + random.uniform(-0, 0)
            interp_x, interp_y = self._adjust_to_screen_bounds(
                interp_x, interp_y, driver.get_window_size()["width"], driver.get_window_size()["height"]
            )
            move_duration = int(duration / steps)
            finger.create_pointer_move(x=interp_x, y=interp_y, duration=move_duration)

        finger.create_pointer_up(button=MouseButton.LEFT)
        actions.perform()

    @keyword("Scroll To Element")
    def scroll_into_element(self, locator, max_swipes=5, direction="down", swipe_distance_ratio=0.4,
                            duration=500, container_locator=None):
        """
        Swipes vertically or horizontally (optionally within a container element) until the target element is visible.

        Args:
            locator (str): Target element to find.
            max_swipes (int): Maximum number of swipes to attempt.
            direction (str): 'down', 'up', 'left', or 'right'.
            swipe_distance_ratio (float): Fraction of screen/container size to swipe (0.1 to 0.99).
            duration (int): Duration of the swipe in milliseconds.
            container_locator (str): Optional. Element within which the swipe should be confined.
        """


        if not isinstance(locator, str) or "=" not in locator:
            raise ValueError(
                f"Invalid locator format: '{locator}'. Expected 'strategy=value' (e.g., 'id=elementId').")
        supported_strategies = ["id", "xpath", "accessibility_id", "class_name"]
        strategy = locator.split("=")[0].strip().lower()
        if strategy not in supported_strategies:
            raise ValueError(
                f"Unsupported locator strategy '{strategy}'. Supported: {supported_strategies}.")


        if not isinstance(max_swipes, int):
            raise ValueError("Parameter 'max_swipes' must be an integer.")
        if max_swipes <= 0:
            raise ValueError("Parameter 'max_swipes' must be greater than 0.")


        direction = direction.lower()
        valid_directions = ["down", "up", "left", "right"]
        if direction not in valid_directions:
            raise ValueError(
                f"Invalid direction '{direction}'. Must be one of {valid_directions}.")

        if not isinstance(swipe_distance_ratio, (int, float)):
            raise ValueError(
                "Parameter 'swipe_distance_ratio' must be numeric (float or int).")
        if not (0.1 <= swipe_distance_ratio <= 0.99):
            raise ValueError(
                "Swipe distance ratio must be between 0.1 and 0.99.")

        # duration validation
        if not isinstance(duration, int):
            raise ValueError("Parameter 'duration' must be an integer (milliseconds).")
        if duration <= 0:
            raise ValueError("Parameter 'duration' must be greater than 0.")
        if duration > 5000:
            warnings.warn(
                f"Duration {duration}ms is unusually long; consider values below 5000ms for performance.")

        # container_locator validation (optional)
        if container_locator:
            if not isinstance(container_locator, str) or "=" not in container_locator:
                raise ValueError(
                    f"Invalid container locator format: '{container_locator}'. Expected 'strategy=value'.")
            strategy_c = container_locator.split("=")[0].strip().lower()
            if strategy_c not in supported_strategies:
                raise ValueError(
                    f"Unsupported container locator strategy '{strategy_c}'. Supported: {supported_strategies}.")
            # Verifica existência
            appium_lib = self._builtin.get_library_instance("AppiumLibrary")
            container_element = appium_lib._element_find(container_locator, True, True)
            if not container_element:
                raise RuntimeError(f"Container element not found for locator: {container_locator}")

        # --- End of validation section ---

        driver = self.driver
        screen_size = driver.get_window_size()
        screen_width = screen_size["width"]
        screen_height = screen_size["height"]

        if container_locator:
            self._builtin.log(f"Using swipe area from container: {container_locator}", "INFO")
            x, y, width, height, center_x, center_y = self._get_element_area_center(container_locator)
        else:
            self._builtin.log("Using entire screen for swipe", "INFO")
            x, y, width, height = 0, 0, screen_width, screen_height
            center_x = screen_width // 2
            center_y = screen_height // 2

        swipe_distance_x = swipe_distance_ratio * width
        swipe_distance_y = swipe_distance_ratio * height

        if direction == "down":
            start_x, end_x = center_x, center_x
            start_y = y + height // 2 + swipe_distance_y / 2
            end_y = y + height // 2 - swipe_distance_y / 2
        elif direction == "up":
            start_x, end_x = center_x, center_x
            start_y = y + height // 2 - swipe_distance_y / 2
            end_y = y + height // 2 + swipe_distance_y / 2
        elif direction == "right":
            start_y, end_y = center_y, center_y
            start_x = x + width // 2 + swipe_distance_x / 2
            end_x = x + width // 2 - swipe_distance_x / 2
        elif direction == "left":
            start_y, end_y = center_y, center_y
            start_x = x + width // 2 - swipe_distance_x / 2
            end_x = x + width // 2 + swipe_distance_x / 2

        start_x, start_y = int(start_x), int(start_y)
        end_x, end_y = int(end_x), int(end_y)

        for attempt in range(max_swipes):
            self._builtin.log(f"[SwipeAttempt {attempt + 1}] Trying to locate '{locator}'", "DEBUG")

            if self._is_element_visible(locator):
                self._builtin.log(f"Element '{locator}' found on attempt {attempt + 1}", "INFO")
                return

            self._builtin.log(f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y})", "DEBUG")
            self._perform_scroll(start_x, start_y, end_x, end_y, duration=duration)
            time.sleep(0.5)

        raise RuntimeError(f"Element '{locator}' not found after {max_swipes} swipe attempts.")
