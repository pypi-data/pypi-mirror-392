from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.action_chains import ActionChains


class PerformLongPress:
    """
    Library for performing long press actions on elements using Appium.
    Provides keywords for mobile automation requiring long press gestures.
    """

    def __init__(self):
        """
        Initializes the AppiumLongPressExtensions library and sets up the BuiltIn instance.
        """
        self._builtin = BuiltIn()

    @property
    def _driver(self):
        """
        Returns the current Appium driver instance from AppiumLibrary.
        """
        return self._builtin.get_library_instance('AppiumLibrary')._current_application()

    @keyword("Perform Long Press")
    def perform_long_press(self, locator, duration=1000):
        """Perform a long press gesture on a mobile element.

        Locates an element using the given locator strategy and value, then
        performs a long press gesture on it for the specified duration.

        [Arguments]
        locator    Element locator in format 'strategy=value'. Supported strategies:
                  id, xpath, accessibility_id, class name, css selector, name
        duration   Time in milliseconds to hold the press (default 1000)

        [Return Values]
        None. Passes if gesture is performed successfully.

        [Raises]
        ValueError     If locator is None, empty or malformed
                      If strategy is not supported
                      If element cannot be found
                      If duration is not a positive number
        RuntimeError   If Appium driver is not initialized
                      If gesture cannot be performed
        """
        driver = self._driver

        locator_parts = locator.split('=', 1)
        if len(locator_parts) != 2:
            raise ValueError("Locator must be in 'strategy=value' format")

        strategy, value = locator_parts


        element = driver.find_element(strategy, value)


        actions = ActionChains(driver)
        actions.click_and_hold(element).pause(duration/1000).release().perform()

