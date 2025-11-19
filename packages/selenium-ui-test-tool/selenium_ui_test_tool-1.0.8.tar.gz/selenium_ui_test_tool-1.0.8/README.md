# Selenium UI Test Tool

Bibliothèque Python pour faciliter les tests UI automatisés avec Selenium WebDriver.

## 📋 Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Reference](#api-reference)
- [Exemples](#exemples)
- [Contribuer](#contribuer)

## 🚀 Installation

### Installation depuis PyPI (quand publié)

```bash
pip install selenium-ui-test-tool
```

### Installation depuis le code source

```bash
git clone <repository-url>
cd selenium_ui_test_tool
pip install -e .
```

### Dépendances

- Python >= 3.8
- Selenium >= 4.15.0
- python-dotenv >= 1.0.0
- webdriver-manager >= 4.0.1

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine de votre projet avec les variables nécessaires :

```env
# Exemple de configuration
CHROMEDRIVER_PATH=/path/to/chromedriver  # Optionnel
HEADLESS=false  # true pour exécuter en mode headless
CI=false  # true si exécuté en CI/CD
```

### Configuration ChromeDriver

La bibliothèque gère automatiquement ChromeDriver de plusieurs façons :

1. **Variable d'environnement** : Si `CHROMEDRIVER_PATH` est défini, elle l'utilise
2. **webdriver-manager** : Télécharge et gère automatiquement la version appropriée
3. **Fallback** : Utilise `/opt/homebrew/bin/chromedriver` (macOS Homebrew)

## 📖 Utilisation

### Exemple basique

```python
from selenium_ui_test_tool import BaseTest
from selenium.webdriver.common.by import By

def test_example(driver):
    """Fonction de test qui retourne True si le test réussit"""
    # Votre logique de test ici
    title = driver.title
    return "Example" in title

# Créer et exécuter le test
test = BaseTest(
    test_function=test_example,
    success_message="✅ Test réussi !",
    failure_message="❌ Test échoué !",
    url="https://example.com",
    exit_on_failure=True
)

test.run()
```

### Utilisation des utilitaires

```python
from selenium_ui_test_tool import (
    create_driver,
    get_url,
    wait_for_element,
    configure_actions,
    click_element,
    click_on,
    fill_input,
    fill_login_form,
    fill_login_form_with_confirm_password,
    get_env_var
)
from selenium.webdriver.common.by import By

# Créer un driver
driver = create_driver(headless=False)

# Naviguer vers une URL
get_url(driver, "https://example.com")

# Attendre un élément
element = wait_for_element(driver, By.ID, "my-element", timeout=10)

# Configurer et exécuter une action
success = configure_actions(driver, By.CSS_SELECTOR, ".my-button")

# Cliquer sur un élément avec messages personnalisés
click_element(driver, By.ID, "submit-button", 
              success_message="Bouton cliqué avec succès",
              error_message="Impossible de cliquer sur le bouton")

# Créer un store d'actions avec click_on
ticket_actions = [
    (By.XPATH, "//span[contains(text(),'Annuel')]", "Section annuelle sélectionnée"),
    (By.XPATH, "//span[contains(text(),'Le Pass Annuel')]", "Le Pass Annuel sélectionné"),
]

for by, selector, success_message in ticket_actions:
    click_on(
        driver,
        by,
        selector,
        success_message=success_message,
        error_message=f"Impossible de cliquer sur {selector}"
    )

# Remplir un champ de formulaire
fill_input(driver, By.ID, "username", "mon_utilisateur")

# Remplir un formulaire de connexion complet
fill_login_form(
    driver,
    username_env="LOGIN_USERNAME",
    password_env="LOGIN_PASSWORD",
    by=By.ID,
    selector="login-form",
    button="login-button"
)

# Récupérer une variable d'environnement
username = get_env_var("LOGIN_USERNAME", required=True)

# N'oubliez pas de fermer le driver
driver.quit()
```

## 📚 API Reference

### `BaseTest`

Classe principale pour exécuter des tests UI automatisés.

#### Constructeur

```python
BaseTest(
    test_function: Callable[[WebDriver], bool],
    success_message: str,
    failure_message: str,
    url: str,
    exit_on_failure: bool = True
)
```

**Paramètres :**

- `test_function` : Fonction qui prend un `WebDriver` en paramètre et retourne un `bool` indiquant le succès du test
- `success_message` : Message affiché si le test réussit
- `failure_message` : Message affiché si le test échoue
- `url` : URL à charger dans le navigateur
- `exit_on_failure` : Si `True`, le programme s'arrête avec le code 1 en cas d'échec

#### Méthodes

- `setup()` : Initialise le driver et charge l'URL
- `teardown()` : Ferme le driver
- `run()` : Exécute le test complet (setup → test → teardown)

### `create_driver(headless: bool = False) -> WebDriver`

Crée et configure une instance de Chrome WebDriver.

**Paramètres :**

- `headless` : Si `True`, le navigateur s'exécute en mode headless

**Retourne :** Instance de `selenium.webdriver.chrome.webdriver.WebDriver`

### `get_url(driver: WebDriver, url: str) -> None`

Navigue vers une URL donnée.

**Paramètres :**

- `driver` : Instance de WebDriver
- `url` : URL à charger

### `wait_for_element(driver: WebDriver, by: By, selector: str, timeout: int = 10) -> WebElement | None`

Attend qu'un élément soit présent dans le DOM.

**Paramètres :**

- `driver` : Instance de WebDriver
- `by` : Stratégie de localisation (ex: `By.ID`, `By.CSS_SELECTOR`)
- `selector` : Sélecteur de l'élément
- `timeout` : Temps d'attente maximum en secondes (défaut: 10)

**Retourne :** L'élément trouvé ou `None` si timeout

### `configure_actions(driver: WebDriver, by: By, selector: str) -> bool`

Configure et exécute une action sur un élément (scroll + click).

**Paramètres :**

- `driver` : Instance de WebDriver
- `by` : Stratégie de localisation
- `selector` : Sélecteur de l'élément

**Retourne :** `True` si l'action a réussi, `False` sinon

### `click_element(driver: WebDriver, by: By, selector: str, wait_before_click: int = 0, success_message: str | None = None, error_message: str | None = None, verify_before_click: bool = True) -> bool`

Clique sur un élément avec des fonctionnalités avancées (attente, messages personnalisés, vérification).

**Paramètres :**

- `driver` : Instance de WebDriver
- `by` : Stratégie de localisation (ex: `By.ID`, `By.CSS_SELECTOR`)
- `selector` : Sélecteur de l'élément
- `wait_before_click` : Temps d'attente en secondes avant de cliquer (défaut: 0)
- `success_message` : Message à afficher en cas de succès (optionnel)
- `error_message` : Message à afficher en cas d'erreur (optionnel)
- `verify_before_click` : Si `True`, vérifie que l'élément existe avant de cliquer (défaut: `True`)

**Retourne :** `True` si le clic a réussi, `False` sinon

**Exemple :**
```python
# Cliquer avec un message de succès
click_element(driver, By.ID, "submit-btn", 
              success_message="Formulaire soumis avec succès")

# Cliquer après une attente
click_element(driver, By.CSS_SELECTOR, ".button", 
              wait_before_click=2,
              error_message="Impossible de cliquer sur le bouton")
```

### `click_on(driver: WebDriver, by: By, selector: str, success_message: str, error_message: str) -> bool`

Couche utilitaire basée sur `click_element` pour créer rapidement des fonctions d'actions regroupées dans un store.

**Paramètres :**

- `driver` : Instance de WebDriver
- `by` / `selector` : Stratégie et sélecteur de l'élément
- `success_message` : Message affiché en cas de succès
- `error_message` : Message affiché en cas d'échec

**Cas d'usage :** créer un dictionnaire ou une liste d'actions réutilisables.

```python
from selenium_ui_test_tool import click_on
from selenium.webdriver.common.by import By

TICKET_ACTIONS = [
    (By.XPATH, "//span[contains(text(),'Annuel')]", "Section Annuel cliquée"),
    (By.XPATH, "//span[contains(text(),'Le Pass Annuel')]", "Pass annuel sélectionné"),
]

def monthly_buying(driver):
    for by, selector, success in TICKET_ACTIONS:
        click_on(
            driver,
            by,
            selector,
            success_message=success,
            error_message=f"Impossible de cliquer sur {selector}"
        )
```

### `fill_input(driver: WebDriver, by: By, selector: str, value: str, timeout: int = 10) -> bool`

Remplit un champ de formulaire avec scroll automatique vers l'élément.

**Paramètres :**

- `driver` : Instance de WebDriver
- `by` : Stratégie de localisation (ex: `By.ID`, `By.CSS_SELECTOR`)
- `selector` : Sélecteur de l'élément
- `value` : Valeur à saisir dans le champ
- `timeout` : Temps d'attente maximum en secondes (défaut: 10)

**Retourne :** `True` si le remplissage a réussi, `False` sinon

**Exemple :**
```python
# Remplir un champ username
fill_input(driver, By.ID, "username", "mon_utilisateur")

# Remplir un champ email
fill_input(driver, By.CSS_SELECTOR, "input[type='email']", "email@example.com")
```

### `fill_login_form(driver: WebDriver, username_env: str = "LOGIN_USERNAME", password_env: str = "LOGIN_PASSWORD", by: str = "id", selector: str = "test", button: str = "test") -> bool`

Remplit automatiquement un formulaire de connexion en utilisant les variables d'environnement pour le username et le password, puis clique sur le bouton de connexion.

**Paramètres :**

- `driver` : Instance de WebDriver
- `username_env` : Nom de la variable d'environnement pour le username (défaut: "LOGIN_USERNAME")
- `password_env` : Nom de la variable d'environnement pour le password (défaut: "LOGIN_PASSWORD")
- `by` : Stratégie de localisation pour les champs (défaut: "id")
- `selector` : Sélecteur des champs de formulaire
- `button` : Sélecteur du bouton de connexion

**Retourne :** `True` si le formulaire a été rempli et soumis avec succès, `False` sinon

**Exemple :**
```python
# Utilisation avec les variables d'environnement par défaut
fill_login_form(
    driver,
    by=By.ID,
    selector="login-form",
    button="login-button"
)
```

### `fill_login_form_with_confirm_password(driver: WebDriver, username_env: str = "LOGIN_USERNAME", password_env: str = "LOGIN_PASSWORD", by: str = "id", selector: str = "test", button: str = "test") -> bool`

Remplit automatiquement un formulaire de connexion avec confirmation de mot de passe en utilisant les variables d'environnement.

**Paramètres :**

- `driver` : Instance de WebDriver
- `username_env` : Nom de la variable d'environnement pour le username (défaut: "LOGIN_USERNAME")
- `password_env` : Nom de la variable d'environnement pour le password (défaut: "LOGIN_PASSWORD")
- `by` : Stratégie de localisation pour les champs (défaut: "id")
- `selector` : Sélecteur des champs de formulaire
- `button` : Sélecteur du bouton de connexion

**Retourne :** `True` si le formulaire a été rempli et soumis avec succès, `False` sinon

**Exemple :**
```python
# Formulaire avec confirmation de mot de passe
fill_login_form_with_confirm_password(
    driver,
    by=By.ID,
    selector="register-form",
    button="register-button"
)
```

### `get_env_var(name: str, required: bool = True) -> str | None`

Récupère une variable d'environnement.

**Paramètres :**

- `name` : Nom de la variable d'environnement
- `required` : Si `True`, lève une exception si la variable n'est pas trouvée

**Retourne :** Valeur de la variable ou `None` si non trouvée et `required=False`

**Lève :** `ValueError` si la variable est requise mais non trouvée

## 💡 Exemples

### Exemple complet : Test de connexion (avec `fill_login_form`)

```python
from selenium_ui_test_tool import BaseTest, fill_login_form, wait_for_element
from selenium.webdriver.common.by import By

def test_login(driver):
    """Test de connexion à une application avec fill_login_form"""
    # Remplir et soumettre le formulaire de connexion automatiquement
    if not fill_login_form(
        driver,
        username_env="LOGIN_USERNAME",
        password_env="LOGIN_PASSWORD",
        by=By.ID,
        selector="login-form",
        button="login-button"
    ):
        return False
    
    # Vérifier que la connexion a réussi
    welcome_message = wait_for_element(driver, By.CLASS_NAME, "welcome", timeout=5)
    return welcome_message is not None

# Exécuter le test
test = BaseTest(
    test_function=test_login,
    success_message="✅ Connexion réussie !",
    failure_message="❌ Échec de la connexion",
    url="https://example.com/login",
    exit_on_failure=True
)

test.run()
```

### Exemple : Test de connexion manuel (avec `fill_input`)

```python
from selenium_ui_test_tool import BaseTest, fill_input, click_element, get_env_var
from selenium.webdriver.common.by import By

def test_login_manual(driver):
    """Test de connexion avec remplissage manuel des champs"""
    # Remplir le champ username
    if not fill_input(driver, By.ID, "username", get_env_var("LOGIN_USERNAME")):
        return False
    
    # Remplir le champ password
    if not fill_input(driver, By.ID, "password", get_env_var("LOGIN_PASSWORD")):
        return False
    
    # Cliquer sur le bouton de connexion
    return click_element(
        driver, 
        By.ID, 
        "login-button",
        success_message="Connexion réussie",
        error_message="Échec de la connexion"
    )

# Exécuter le test
test = BaseTest(
    test_function=test_login_manual,
    success_message="✅ Connexion réussie !",
    failure_message="❌ Échec de la connexion",
    url="https://example.com/login",
    exit_on_failure=True
)

test.run()
```

### Exemple : Store d'actions avec `click_on`

```python
from selenium_ui_test_tool import BaseTest, click_on
from selenium.webdriver.common.by import By
import time

ACTIONS_MONTHLY = [
    (By.XPATH, "//span[contains(text(),'Annuel')]", "Section Annuel ouverte"),
    (By.XPATH, "//span[contains(text(),'Le Pass Annuel')]", "Pass annuel sélectionné"),
]

def monthly_buying(driver):
    for by, selector, success in ACTIONS_MONTHLY:
        click_on(
            driver,
            by,
            selector,
            success_message=success,
            error_message=f"Impossible de cliquer sur {selector}"
        )

def buying_helper_monthly(driver):
    time.sleep(2)
    monthly_buying(driver)
    return True

test = BaseTest(
    test_function=buying_helper_monthly,
    success_message="✅ Achat mensuel réussi",
    failure_message="❌ Échec du parcours d'achat",
    url="https://example.com/store"
)

test.run()
```

### Exemple : Utilisation en mode headless

```python
from selenium_ui_test_tool import create_driver, get_url
import os

# Définir le mode headless via variable d'environnement
os.environ["HEADLESS"] = "true"

driver = create_driver(headless=True)
get_url(driver, "https://example.com")

# Votre code de test ici

driver.quit()
```

### Exemple : Gestion des erreurs

```python
from selenium_ui_test_tool import BaseTest, wait_for_element
from selenium.webdriver.common.by import By

def test_with_error_handling(driver):
    """Test avec gestion d'erreurs robuste"""
    try:
        element = wait_for_element(driver, By.ID, "my-element", timeout=5)
        if element is None:
            print("⚠️ Élément non trouvé")
            return False
        
        # Votre logique de test
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

test = BaseTest(
    test_function=test_with_error_handling,
    success_message="✅ Test réussi",
    failure_message="❌ Test échoué",
    url="https://example.com",
    exit_on_failure=False  # Ne pas arrêter le programme en cas d'échec
)

test.run()
```

## 🔧 Mode CI/CD

La bibliothèque détecte automatiquement si elle s'exécute en environnement CI/CD via la variable d'environnement `CI=true`. En mode CI :

- Le navigateur s'exécute automatiquement en mode headless
- Les variables d'environnement sont lues depuis les secrets GitHub Actions (ou équivalent)
- Pas de pause interactive après l'exécution

### Configuration GitHub Actions

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install selenium-ui-test-tool
      - name: Run tests
        env:
          CI: true
          LOGIN_USERNAME: ${{ secrets.LOGIN_USERNAME }}
          LOGIN_PASSWORD: ${{ secrets.LOGIN_PASSWORD }}
        run: |
          python your_test_script.py
```

## 📝 Structure du projet

```
selenium_ui_test_tool/
├── selenium_ui_test_tool/
│   ├── __init__.py
│   ├── base_test/
│   │   ├── __init__.py
│   │   └── base_test.py
│   ├── click_element/
│   │   ├── __init__.py
│   │   └── click_element.py
│   ├── config_actions/
│   │   ├── __init__.py
│   │   └── config_actions.py
│   ├── driver_builder/
│   │   ├── __init__.py
│   │   └── driver_builder.py
│   ├── get_env_var/
│   │   ├── __init__.py
│   │   └── get_env_var.py
│   ├── get_url/
│   │   ├── __init__.py
│   │   └── get_url.py
│   └── wait_element/
│       ├── __init__.py
│       └── wait_elements.py
├── pyproject.toml
├── setup.py
├── requirements.txt
├── README.md
└── env.example
```

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📄 Auteur

Yann Dipita

## 🐛 Signaler un bug

Si vous trouvez un bug, veuillez ouvrir une issue sur GitHub avec :
- Une description claire du bug
- Les étapes pour reproduire
- Le comportement attendu vs le comportement actuel
- Votre environnement (OS, Python, Selenium versions)

## 📧 Contact

Pour toute question, contactez dipitay@gmail.com.

---

**Note :** Cette bibliothèque est en développement actif. L'API peut changer entre les versions mineures.

