"""
Exemple d'utilisation de la bibliothèque Selenium UI Test Tool

Ce script montre comment utiliser les différentes fonctionnalités de la bibliothèque.
"""

from selenium_ui_test_tool import (
    BaseTest,
    create_driver,
    get_url,
    wait_for_element,
    configure_actions,
    get_env_var
)
from selenium.webdriver.common.by import By


def example_basic_test(driver):
    """
    Exemple de test basique qui vérifie le titre de la page.
    """
    title = driver.title
    print(f"Titre de la page : {title}")
    return "Example" in title or "Google" in title


def example_login_test(driver):
    """
    Exemple de test de connexion (nécessite des variables d'environnement).
    """
    try:
        # Récupérer les credentials depuis les variables d'environnement
        username = get_env_var("LOGIN_USERNAME", required=False)
        password = get_env_var("LOGIN_PASSWORD", required=False)
        
        if not username or not password:
            print("⚠️ Variables d'environnement LOGIN_USERNAME et LOGIN_PASSWORD non définies")
            return False
        
        # Attendre et remplir le champ username
        username_field = wait_for_element(driver, By.ID, "username", timeout=5)
        if username_field:
            username_field.send_keys(username)
        else:
            print("❌ Champ username non trouvé")
            return False
        
        # Attendre et remplir le champ password
        password_field = wait_for_element(driver, By.ID, "password", timeout=5)
        if password_field:
            password_field.send_keys(password)
        else:
            print("❌ Champ password non trouvé")
            return False
        
        # Cliquer sur le bouton de connexion
        if configure_actions(driver, By.ID, "login-button"):
            print("✅ Bouton de connexion cliqué")
        else:
            print("❌ Impossible de cliquer sur le bouton de connexion")
            return False
        
        # Vérifier que la connexion a réussi (attendre un élément de confirmation)
        welcome_message = wait_for_element(driver, By.CLASS_NAME, "welcome", timeout=5)
        return welcome_message is not None
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False


def example_manual_driver_usage():
    """
    Exemple d'utilisation manuelle du driver sans BaseTest.
    """
    driver = None
    try:
        # Créer le driver
        driver = create_driver(headless=False)
        
        # Naviguer vers une URL
        get_url(driver, "https://www.example.com")
        
        # Attendre un élément
        element = wait_for_element(driver, By.TAG_NAME, "h1", timeout=10)
        if element:
            print(f"✅ Élément trouvé : {element.text}")
        else:
            print("❌ Élément non trouvé")
        
        # Exécuter une action
        if configure_actions(driver, By.TAG_NAME, "a"):
            print("✅ Action exécutée avec succès")
        else:
            print("❌ Action échouée")
            
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("Exemples d'utilisation de Selenium UI Test Tool")
    print("=" * 60)
    
    # Exemple 1 : Test basique avec BaseTest
    print("\n1. Test basique avec BaseTest")
    print("-" * 60)
    test1 = BaseTest(
        test_function=example_basic_test,
        success_message="✅ Test basique réussi !",
        failure_message="❌ Test basique échoué !",
        url="https://www.example.com",
        exit_on_failure=False
    )
    test1.run()
    
    # Exemple 2 : Utilisation manuelle du driver
    print("\n2. Utilisation manuelle du driver")
    print("-" * 60)
    example_manual_driver_usage()
    
    # Exemple 3 : Test de connexion (nécessite des variables d'environnement)
    # Décommentez pour tester
    # print("\n3. Test de connexion")
    # print("-" * 60)
    # test2 = BaseTest(
    #     test_function=example_login_test,
    #     success_message="✅ Connexion réussie !",
    #     failure_message="❌ Échec de la connexion",
    #     url="https://example.com/login",
    #     exit_on_failure=False
    # )
    # test2.run()
    
    print("\n" + "=" * 60)
    print("Exemples terminés")
    print("=" * 60)

