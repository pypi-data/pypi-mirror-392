"""
Swipe Element Library — Robot Framework + Appium 

Performs swipes (`mobile: dragGesture`) on elements with configurable `direction`,
`percent` (0.01-2.0) and `speed` (ms). Applies a fixed 5% start margin.
Reuses the active AppiumLibrary session.
"""

from appium.webdriver.common.appiumby import AppiumBy
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

class SwipeElement:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # Access to Robot Framework's built-in library
        self._builtin = BuiltIn()

    @property
    def driver(self):
        # Get the current Appium driver instance from AppiumLibrary
        return self._builtin.get_library_instance("AppiumLibrary")._current_application()

    @keyword("Swipe Element")
    def swipe_element(self, *args, **kwargs):
        """
        Perform a directional swipe on a single UI element using `mobile: dragGesture` with a fixed 5% start margin.

        [Arguments]
        - locator: (str) Target element locator. Can be a single positional string like `xpath=//...`
          or a named argument using one of: `id`, `xpath`, `accessibility_id`, `class_name`,
          `android_uiautomator`, `ios_predicate`, `ios_class_chain`, `name`.
        - direction: (str) One of `up`, `down`, `left`, `right`. Default: `right`.
        - percent: (float) Distance as a fraction of the element size in `0.01..2.0`.
          Values > 1.0 allow movement beyond the element bounds. Default: `0.5`.
        - speed: (int) Gesture speed in milliseconds for `mobile: dragGesture`. Must be positive. Default: `800`.

        [Return Values]
        - None

        [Raises]
        - ValueError: Invalid locator, unsupported direction, or percent out of range.
        - TypeError: Parameters that cannot be converted to expected types.
        - RuntimeError: Driver/runtime failures may propagate from the underlying call.
        """

        # Mapping of supported locator strategies
        locator_keys = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "class_name": AppiumBy.CLASS_NAME,
            "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
            "ios_predicate": AppiumBy.IOS_PREDICATE,
            "ios_class_chain": AppiumBy.IOS_CLASS_CHAIN,
            "name": AppiumBy.NAME,
        }

        locator_type = None
        locator_value = None

        # Try to get locator from keyword arguments
        for key in kwargs:
            if key.lower() in locator_keys:
                locator_type = key.lower()
                locator_value = kwargs[key]
                break

        # If not found in kwargs, try from positional arguments
        if not locator_type and args:
            raw = args[0].strip()
            if "=" in raw:
                locator_type, locator_value = raw.split("=", 1)
                locator_type = locator_type.lower()
            elif raw.startswith("//"):
                locator_type = "xpath"
                locator_value = raw

        # Validate locator
        if not locator_type or locator_type not in locator_keys or not locator_value:
            raise ValueError("Invalid locator. Use xpath=..., id=..., or a valid locator format.")

        # Read optional parameters
        direction = kwargs.get("direction", "right")
        percent = float(kwargs.get("percent", 0.5))
        speed = int(kwargs.get("speed", 800))

        # Validate parameters
        if direction not in ["up", "down", "left", "right"]:
            raise ValueError("Invalid direction. Use: 'up', 'down', 'left', or 'right'.")
        if not (0.01 <= percent <= 2.0):
            raise ValueError("Percent must be between 0.01 and 2.0.")
        if speed <= 0:
            raise ValueError("Speed must be a positive integer.")

        # Find element and get its dimensions
        driver = self.driver
        strategy = locator_keys[locator_type]
        element = driver.find_element(strategy, locator_value)
        rect = element.rect

        # Set a fixed start margin to avoid touching the edge of the element
        start_margin = 0.05

        # Calculate coordinates and perform drag based on direction
        if direction in ["left", "right"]:
            start_x = rect["x"] + rect["width"] * start_margin
            end_x = rect["x"] + rect["width"] * percent
            y = rect["y"] + rect["height"] / 2

            driver.execute_script(
                "mobile: dragGesture",
                {"startX": round(start_x), "startY": round(y), "endX": round(end_x), "endY": round(y), "speed": speed},
            )

        elif direction in ["up", "down"]:
            start_y = rect["y"] + rect["height"] * start_margin
            end_y = rect["y"] + rect["height"] * percent
            x = rect["x"] + rect["width"] / 2

        # Invert only for 'up' (Y axis increases downward)
        if direction == "up":
            start_y, end_y = end_y, start_y

            driver.execute_script(
                "mobile: dragGesture",
                {"startX": round(x), "startY": round(start_y), "endX": round(x), "endY": round(end_y), "speed": speed},
            )
        # Log success
        self._builtin.log(f"[SUCCESS] Drag performed to {direction} with percent={percent}, speed={speed}", "INFO")
