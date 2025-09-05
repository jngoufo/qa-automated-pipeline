# Fichier: src/pipeline.py

import pandas as pd
from sqlalchemy import create_engine, text
import yfinance as yf
from datetime import datetime
import pytz
import os

def get_current_montreal_date():
    """Retourne la date actuelle à Montréal. Facile à mocker."""
    utc_now = datetime.now(pytz.utc)
    montreal_tz = pytz.timezone('America/Montreal')
    return utc_now.astimezone(montreal_tz).date()

# --- Fonctions Utilitaires (testées unitairement) ---

def translate_ticker(ticker):
    """Traduit les tickers canadiens pour yfinance."""
    if ticker.startswith('TSE:'):
        return ticker.split(':')[1].replace('.', '-') + '.TO'
    return ticker

def read_and_clean_csv(file_path):
    """
    Lit un fichier CSV, nettoie les noms des colonnes et la colonne 'price'.
    Gère le cas où le fichier est vide.
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return pd.DataFrame()
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

    df.columns = df.columns.str.strip().str.lower()
    if 'price' in df.columns:
        df['price'] = df['price'].astype(str).str.replace(r'[C$]', '', regex=True).astype(float)
    return df

def enrich_data_with_yfinance(df):
    """
    Prend un DataFrame et ajoute/met à jour une colonne 'market_price'
    en interrogeant l'API yfinance.
    """
    if df.empty:
        return df

    for index, row in df.iterrows():
        ticker_symbol = row['ticker']
        translated_symbol = translate_ticker(ticker_symbol)
        try:
            ticker_data = yf.Ticker(translated_symbol)
            market_price = ticker_data.info['regularMarketPrice']
            df.loc[index, 'market_price'] = market_price
        except Exception as e:
            print(f"Erreur yfinance pour {ticker_symbol} (traduit en {translated_symbol}): {e}")
            df.loc[index, 'market_price'] = row['price']
    return df

def synchronize_database(df, engine):
    """
    Compare les tickers du DataFrame avec ceux en base et supprime les titres obsolètes.
    """
    if df.empty:
        print("Fichier CSV vide ou invalide, aucune synchronisation effectuée pour éviter une suppression accidentelle.")
        return

    csv_tickers = set(df['ticker'].str.lower())
    with engine.connect() as connection:
        with connection.begin():
            result = connection.execute(text("SELECT id, ticker FROM titres"))
            db_tickers = {row.ticker.lower(): row.id for row in result}
            tickers_to_delete = set(db_tickers.keys()) - csv_tickers

            if tickers_to_delete:
                print(f"Tickers à supprimer : {tickers_to_delete}")
                ids_to_delete = [db_tickers[ticker] for ticker in tickers_to_delete]
                connection.execute(
                    text("DELETE FROM titres WHERE id IN :ids"),
                    {"ids": ids_to_delete}
                )

def insert_data(df, engine, execution_date):
    """
    Insère ou met à jour les données des tables 'titres' et 'historique'.
    """
    if df.empty:
        return

    with engine.connect() as connection:
        with connection.begin():
            for _, row in df.iterrows():
                res = connection.execute(
                    text("SELECT id FROM titres WHERE ticker = :ticker"),
                    {"ticker": row['ticker']}
                ).first()
                
                if res:
                    titre_id = res[0]
                else:
                    insert_res = connection.execute(
                        text("INSERT INTO titres (ticker, nom_entreprise) VALUES (:ticker, :nom)"),
                        {"ticker": row['ticker'], "nom": row['nom_entreprise']}
                    )
                    titre_id = insert_res.lastrowid
                
                # S'assurer que 'market_price' existe avant de l'utiliser
                price_to_use = row.get('market_price', row.get('price', 0))

                connection.execute(
                    text("""
                        INSERT INTO historique (titre_id, date, valeur)
                        VALUES (:titre_id, :date, :valeur)
                        ON DUPLICATE KEY UPDATE valeur = :valeur
                    """),
                    {
                        "titre_id": titre_id,
                        "date": execution_date,
                        "valeur": price_to_use * row['no_of_shares']
                    }
                )

# --- L'ORCHESTRATEUR ---
def run_full_pipeline(csv_path, db_engine):
    """
    Fonction principale qui exécute toutes les étapes du pipeline dans le bon ordre.
    """
    # On appelle notre nouvelle fonction pour obtenir la date
    today = get_current_montreal_date()

    if today.weekday() >= 5: # 5=Samedi, 6=Dimanche
        print(f"Exécution ignorée le {today}: nous sommes le week-end.")
        return None

    # Le reste du code ne s'exécute que si ce n'est PAS le week-end
    print("Étape 1: Lecture et nettoyage du fichier CSV...")
    df = read_and_clean_csv(csv_path)

    print("Étape 2: Synchronisation de la base de données...")
    synchronize_database(df, db_engine)

    print("Étape 3: Enrichissement des données via yfinance...")
    df = enrich_data_with_yfinance(df)
    
    print(f"Étape 4: Insertion des données pour la date {today}...")
    insert_data(df, db_engine, today)
    
    print("Pipeline terminé avec succès.")
    return today