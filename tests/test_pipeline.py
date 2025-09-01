# Fichier: tests/test_pipeline.py
from src.pipeline import read_and_clean_csv
import pandas as pd
from sqlalchemy import text
from src.pipeline import insert_data

def test_lecture_et_nettoyage_nominal():
    # GIVEN (Étant donné) - Le chemin vers notre fichier de test
    csv_file_path = "data_fixtures/happy_path.csv"

    # WHEN (Quand) - On exécute la fonction que l'on veut tester
    result_df = read_and_clean_csv(csv_file_path)

    # THEN (Alors) - On vérifie que le résultat est celui attendu
    
    # 1. Vérifier que le DataFrame a bien 2 lignes
    assert len(result_df) == 2, "Le DataFrame devrait contenir 2 lignes"

    # 2. Vérifier que la colonne 'price' est bien un nombre
    assert pd.api.types.is_numeric_dtype(result_df['price']), "La colonne 'price' doit être numérique"
    
    # 3. Vérifier une valeur précise pour être sûr du nettoyage
    msft_price = result_df[result_df['ticker'] == 'MSFT']['price'].iloc[0]
    assert msft_price == 250.50, "Le prix nettoyé de MSFT devrait être 250.50"
    
def test_fichier_csv_vide():
    # GIVEN - Le chemin vers notre fichier CSV vide
    csv_file_path = "data_fixtures/empty.csv"

    # WHEN - On exécute la fonction avec ce fichier
    result_df = read_and_clean_csv(csv_file_path)

    # THEN - On vérifie que le résultat est un DataFrame vide
    assert result_df.empty, "Le DataFrame devrait être vide pour un fichier CSV vide"
    
def test_colonne_price_manquante():
    # GIVEN - Le chemin vers un CSV sans colonne 'price'
    csv_file_path = "data_fixtures/missing_price_column.csv"

    # WHEN - On exécute la fonction
    result_df = read_and_clean_csv(csv_file_path)

    # THEN - On vérifie que le programme n'a pas planté et que la colonne n'existe pas
    assert 'price' not in result_df.columns, "La colonne 'price' ne devrait pas exister dans le résultat"
    assert len(result_df) == 1, "Le DataFrame devrait quand même contenir une ligne"

def test_insertion_base_de_donnees(db_engine):
    # GIVEN - Un DataFrame de test créé à la main
    data = {
        'ticker': ['AAPL', 'GOOGL'],
        'nom_entreprise': ['Apple Inc.', 'Alphabet Inc.']
    }
    test_df = pd.DataFrame(data)

    # WHEN - On exécute la fonction d'insertion en lui passant le moteur de la BDD de test
    insert_data(test_df, db_engine)

    # THEN - On vérifie directement dans la BDD que les données sont là
    with db_engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM titres")).scalar_one()
        assert result == 2, "Il devrait y avoir 2 enregistrements dans la table titres"
        
        apple_name = connection.execute(
            text("SELECT nom_entreprise FROM titres WHERE ticker = 'AAPL'")
        ).scalar_one()
        assert apple_name == "Apple Inc.", "Le nom de l'entreprise pour AAPL est incorrect"