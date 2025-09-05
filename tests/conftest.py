# Fichier: tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
import os

# 1. On définit l'URL de connexion par défaut, celle pour notre environnement Docker local.
DEFAULT_DB_URL = "mysql+pymysql://root:supersecretpassword@localhost:3307/analyste_augmente_test"

# 2. On essaie de lire une variable d'environnement nommée 'DB_TEST_URL'.
#    - Si elle existe (ce sera le cas dans GitHub Actions), on utilise sa valeur.
#    - Si elle n'existe pas (quand tu lances les tests sur ta machine), on utilise la valeur par défaut.
DB_URL_TO_USE = os.getenv("DB_TEST_URL", DEFAULT_DB_URL)

@pytest.fixture(scope="function")
def db_engine():
    """
    Une fixture qui :
    1. Se connecte à la BDD de test en utilisant l'URL flexible (locale ou CI/CD).
    2. CRÉE le schéma en exécutant chaque commande de schema.sql séparément.
    3. Cède la connexion au test.
    """
    # On utilise maintenant notre variable flexible pour créer la connexion
    engine = create_engine(DB_URL_TO_USE)

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        full_sql_script = f.read()

    sql_commands = [cmd for cmd in full_sql_script.split(';') if cmd.strip()]

    with engine.connect() as connection:
        with connection.begin():
            for command in sql_commands:
                connection.execute(text(command))
    
    yield engine