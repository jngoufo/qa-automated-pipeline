# Fichier: tests/conftest.py
import pytest
from sqlalchemy import create_engine, text
import os

# On utilise os.getenv() pour lire les variables d'environnement.
# On fournit des valeurs par défaut pour que ça continue de fonctionner facilement en local.
DB_USER = os.getenv("DB_USER_TEST", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD_TEST", "supersecretpassword")
DB_HOST = os.getenv("DB_HOST_TEST", "localhost")
DB_PORT = os.getenv("DB_PORT_TEST", "3307")
DB_NAME = os.getenv("DB_NAME_TEST", "analyste_augmente_test")

# On reconstruit l'URL de connexion à partir de ces variables.
# C'est beaucoup plus propre et sécurisé.
DB_TEST_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@pytest.fixture
def db_engine():
    """
    Une fixture qui :
    1. Se connecte à la BDD de test.
    2. CRÉE le schéma en exécutant chaque commande de schema.sql séparément.
    3. Cède la connexion au test.
    """
    engine = create_engine(DB_TEST_URL)

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        # On lit tout le fichier SQL
        full_sql_script = f.read()

    # On sépare le script en commandes individuelles en utilisant le point-virgule
    sql_commands = [cmd for cmd in full_sql_script.split(';') if cmd.strip()]

    with engine.connect() as connection:
        with connection.begin():
            # On exécute chaque commande une par une
            for command in sql_commands:
                connection.execute(text(command))
    
    yield engine