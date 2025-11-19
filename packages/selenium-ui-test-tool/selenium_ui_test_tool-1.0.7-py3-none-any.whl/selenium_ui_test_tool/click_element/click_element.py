import time
from selenium_ui_test_tool.config_actions.config_actions import configure_actions
from selenium_ui_test_tool.wait_element.wait_elements import wait_for_element


def click_element(driver, by, selector, wait_before_click=0, success_message=None, error_message=None,
                  verify_before_click=True):
    try:
        if wait_before_click > 0:
            time.sleep(wait_before_click)

        if verify_before_click:
            element = wait_for_element(driver, by, selector)
            if not element:
                if error_message:
                    print(f"⚠️ {error_message}")
                else:
                    print(f"⚠️ Élément non trouvé: {selector}")
                return False

        configure_actions(driver, by, selector)

        # Message de succès
        if success_message:
            print(f"✅ {success_message}")

        return True

    except Exception as e:
        if error_message:
            print(f"⚠️ {error_message}: {e}")
        else:
            print(f"⚠️ Erreur lors du clic sur l'élément {selector}: {e}")
        return False

