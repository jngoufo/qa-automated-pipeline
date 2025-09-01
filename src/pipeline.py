import pandas as pd
from sqlalchemy import text

def read_and_clean_csv(file_path):
    """
    Lit un fichier CSV, nettoie les noms des colonnes et la colonne 'price'.
    Gère le cas où le fichier est vide.
    """
    try:
        df = pd.read_csv(file_path)
        # Si le DataFrame est créé mais est totalement vide (cas d'un fichier avec juste les en-têtes)
        if df.empty:
            return pd.DataFrame() # On retourne un DataFrame vide propre
    except pd.errors.EmptyDataError:
        # Si pandas lève une erreur parce que le fichier est complètement vide
        return pd.DataFrame() # On retourne un DataFrame vide propre

    # Le reste du code ne s'exécute que si le fichier n'est pas vide
    df.columns = df.columns.str.strip().str.lower()
    
    if 'price' in df.columns:
        df['price'] = df['price'].astype(str).str.replace(r'[C$]', '', regex=True).astype(float)
        
    return df


def insert_data(df, engine):
    """
    Insère les données d'un DataFrame dans la table 'titres'.
    Ceci est une version simplifiée pour le test.
    """
    with engine.connect() as connection:
        with connection.begin():
            for index, row in df.iterrows():
                connection.execute(
                    text("INSERT INTO titres (ticker, nom_entreprise) VALUES (:ticker, :nom)"),
                    {"ticker": row['ticker'], "nom": row['nom_entreprise']}
                )