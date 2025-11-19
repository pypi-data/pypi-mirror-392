from selenium.common import TimeoutException
from selenium_ui_test_tool.wait_element.wait_elements import wait_for_element

def configure_actions(driver, by, selector):
    try:
        element = wait_for_element(driver, by, selector)
        if element is None:
            return False
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element.click()
        return True
    except (TimeoutException, AttributeError) as e:
        return False
