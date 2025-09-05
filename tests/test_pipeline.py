# Fichier: tests/test_pipeline.py

import pandas as pd
from sqlalchemy import text
from freezegun import freeze_time
from datetime import date
import pytz
import pytest

# On importe toutes les fonctions que nous allons tester
from src.pipeline import (
    read_and_clean_csv,
    insert_data,
    enrich_data_with_yfinance,
    synchronize_database,
    run_full_pipeline
)

# --- CHAPITRE 1 : Tests sur la lecture des fichiers CSV ---
class TestLectureCSV:
    def test_lecture_et_nettoyage_nominal(self):
        csv_file_path = "data_fixtures/happy_path.csv"
        result_df = read_and_clean_csv(csv_file_path)
        assert len(result_df) == 2
        assert pd.api.types.is_numeric_dtype(result_df['price'])
        msft_price = result_df[result_df['ticker'] == 'MSFT']['price'].iloc[0]
        assert msft_price == 250.50

    def test_fichier_csv_vide(self):
        csv_file_path = "data_fixtures/empty.csv"
        result_df = read_and_clean_csv(csv_file_path)
        assert result_df.empty

    def test_colonne_price_manquante(self):
        csv_file_path = "data_fixtures/missing_price_column.csv"
        result_df = read_and_clean_csv(csv_file_path)
        assert 'price' not in result_df.columns
        assert len(result_df) == 1

# --- CHAPITRE 2 : Tests d'intégration avec la base de données ---
class TestIntegrationDB:
    def test_II_57_insertion_base_de_donnees(self, db_engine):
        data = {
            'ticker': ['AAPL', 'GOOGL'], 
            'nom_entreprise': ['Apple Inc.', 'Alphabet Inc.'],
            'no_of_shares': [10, 5],
            'market_price': [150.0, 200.0]
        }
        test_df = pd.DataFrame(data)
        fake_date = date(2025, 1, 1)
        insert_data(test_df, db_engine, fake_date)
        
        with db_engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM titres")).scalar_one()
            assert result == 2
            apple_name = connection.execute(text("SELECT nom_entreprise FROM titres WHERE ticker = 'AAPL'")).scalar_one()
            assert apple_name == "Apple Inc."

    def test_II_61_synchronisation_suppression_titre(self, db_engine):
        with db_engine.connect() as connection:
            with connection.begin():
                connection.execute(text("INSERT INTO titres (ticker, nom_entreprise) VALUES ('AAPL', 'Apple Inc')"))
                connection.execute(text("INSERT INTO titres (ticker, nom_entreprise) VALUES ('GOOGL', 'Alphabet Inc')"))
        
        csv_path = "data_fixtures/sync_test.csv"
        sync_df = read_and_clean_csv(csv_path)
        synchronize_database(sync_df, db_engine)
        
        with db_engine.connect() as connection:
            titres_count = connection.execute(text("SELECT COUNT(*) FROM titres")).scalar_one()
            assert titres_count == 1
            remaining_ticker = connection.execute(text("SELECT ticker FROM titres")).scalar_one()
            assert remaining_ticker == 'AAPL'

    def test_II_62_synchronisation_insensible_a_la_casse(self, db_engine):
        with db_engine.connect() as connection:
            with connection.begin():
                connection.execute(text("INSERT INTO titres (ticker, nom_entreprise) VALUES ('msft', 'Microsoft Corp')"))

        csv_path = "data_fixtures/case_insensitive_sync.csv"
        sync_df = read_and_clean_csv(csv_path)
        synchronize_database(sync_df, db_engine)
        
        with db_engine.connect() as connection:
            titres_count = connection.execute(text("SELECT COUNT(*) FROM titres")).scalar_one()
            assert titres_count == 1
            remaining_ticker = connection.execute(text("SELECT ticker FROM titres")).scalar_one()
            assert remaining_ticker == 'msft'

# --- CHAPITRE 3 : Tests sur l'enrichissement via API externe ---
class TestEnrichissementAPI:
    def test_II_58_enrichissement_yfinance_succes(self, mocker):
        data = {'ticker': ['AAPL'], 'price': [100.00]}
        test_df = pd.DataFrame(data)
        mock_response = {'regularMarketPrice': 150.55}
        mocker.patch('yfinance.Ticker', return_value=mocker.Mock(info=mock_response))
        enriched_df = enrich_data_with_yfinance(test_df)
        market_price = enriched_df.loc[0, 'market_price']
        assert market_price == 150.55 
    
    def test_II_59_traduction_ticker_canadien_et_enrichissement(self, mocker):
        data = {'ticker': ['TSE:REI.UN'], 'price': [20.00]}
        test_df = pd.DataFrame(data)
        mock_response = {'regularMarketPrice': 20.75, 'currency': 'CAD'}
        mock_yf_ticker = mocker.patch('yfinance.Ticker')
        mock_yf_ticker.return_value.info = mock_response
        
        enriched_df = enrich_data_with_yfinance(test_df)
        
        mock_yf_ticker.assert_called_once_with('REI-UN.TO')
        market_price = enriched_df.loc[0, 'market_price']
        assert market_price == 20.75

    def test_II_60_fallback_si_api_yfinance_echoue(self, mocker):
        data = {'ticker': ['FAKE.TICKER'], 'price': [50.00]}
        test_df = pd.DataFrame(data)
        mocker.patch('yfinance.Ticker', side_effect=Exception("API Error"))
        
        enriched_df = enrich_data_with_yfinance(test_df)
        
        market_price = enriched_df.loc[0, 'market_price']
        assert market_price == 50.00

# --- CHAPITRE 4 : Tests sur la logique métier spécifique ---
class TestLogiqueMetier:
    """
    Regroupe les tests pour les règles métier spécifiques,
    comme la gestion du temps.
    """
    def test_II_63_ignore_execution_le_weekend(self, db_engine, mocker):
        # GIVEN - On mock notre fonction pour qu'elle retourne un samedi
        mocker.patch('src.pipeline.get_current_montreal_date', return_value=date(2025, 9, 6))

        # WHEN
        result = run_full_pipeline("data_fixtures/empty.csv", db_engine)
        
        # THEN
        assert result is None, "Le pipeline ne devrait rien retourner le week-end"

    def test_II_64_date_correcte_avec_fuseau_horaire_montreal(self, db_engine, mocker):
        # GIVEN - On mock notre fonction pour qu'elle retourne la date attendue
        expected_date = date(2024, 10, 24)
        mocker.patch('src.pipeline.get_current_montreal_date', return_value=expected_date)
        
        # WHEN
        result_date = run_full_pipeline("data_fixtures/empty.csv", db_engine)
        
        # THEN
        assert result_date == expected_date