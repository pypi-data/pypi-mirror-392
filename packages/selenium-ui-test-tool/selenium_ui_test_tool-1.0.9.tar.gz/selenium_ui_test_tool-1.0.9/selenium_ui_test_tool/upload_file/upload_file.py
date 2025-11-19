from selenium_ui_test_tool import wait_for_element, get_env_var


def upload_file(driver, file_path, input_selector, by, success_message=None, error_message=None):
    try:
        file = get_env_var(file_path)
        if not file:
            msg = error_message or f"⚠️ Le fichier {file} n'existe pas"
            print(msg)
            return False

        file_input = wait_for_element(driver, by, input_selector)
        if not file_input:
            msg = error_message or "⚠️ Champ de fichier non trouvé"
            print(msg)
            return False

        file_input.send_keys(file)
        msg = success_message or f"✅ Fichier {file} uploadé avec succès"
        print(msg)
        return True

    except Exception as e:
        msg = error_message or f"⚠️ Erreur lors de l'upload: {e}"
        print(msg)
        return False
