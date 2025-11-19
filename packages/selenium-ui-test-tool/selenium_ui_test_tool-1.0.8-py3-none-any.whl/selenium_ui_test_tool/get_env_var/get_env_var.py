import os
from pathlib import Path
from dotenv import load_dotenv


def _find_env_file():
    """
    Cherche le fichier .env en remontant depuis le répertoire de travail courant.
    Cela permet de trouver le .env du projet utilisateur, pas celui de la bibliothèque.
    """
    current_dir = Path.cwd()
    
    # Chercher .env dans le répertoire courant et ses parents
    for path in [current_dir] + list(current_dir.parents):
        env_file = path / ".env"
        if env_file.exists():
            return env_file
    
    return None


# Charger le .env si trouvé, sinon charger depuis le répertoire courant
env_file = _find_env_file()
if env_file:
    load_dotenv(env_file, override=False)
else:
    # Essayer de charger depuis le répertoire courant
    load_dotenv(override=False)


def get_env_var(name: str, required=True):
    value = os.getenv(name)

    if not value and os.getenv("CI") == "true":
        value = os.environ.get(name)

    if required and not value:
        is_ci = os.getenv("CI") == "true"
        env_source = "secrets GitHub" if is_ci else "fichier .env"
        raise ValueError(
            f"⚠️ La variable d'environnement {name} doit être définie ({env_source}).\n"
            f"Vérifiez que le secret {name} est configuré dans GitHub Settings → Secrets and variables → Actions."
        )
    return value
