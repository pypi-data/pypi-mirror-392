from selenium_ui_test_tool.click_element.click_element import click_element


def click_on(driver, by, selector, success_message, error_message):
    return click_element(
        driver,
        by,
        selector,
        success_message=success_message,
        error_message=error_message
    )
