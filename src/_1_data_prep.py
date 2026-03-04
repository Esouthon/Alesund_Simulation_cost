# src/step1_data_prep.py
# Ce module contient une fonction qui lit tes données brutes et retourne le DataFrame
import pandas as pd
import glob
import os
import src.config as cfg

def load_and_prepare_data():
    """
    Parcourt tous les sous-dossiers de data/raw/, lit chaque fichier CSV (colonne unique),
    et reforme le DataFrame complet aligné sur les dates.
    """
    # Cherche tous les fichiers CSV qui sont dans un sous-dossier direct de data/raw/
    # (ex: data/raw/t2m_C/t2m_C.csv OU data/raw/ship/ARTANIA.csv)
    # Adapte le chemin de base en utilisant ton config (ex: cfg.DATA_PATH)
    base_path = cfg.DATA_PATH 
    all_files = glob.glob(os.path.join(base_path, '*', '*.csv'))
    
    if not all_files:
        print("Aucun fichier trouvé dans data/raw/")
        return pd.DataFrame()

    dfs = []
    
    for file in all_files:
        # On lit chaque fichier. L'index sera la Date.
        df_temp = pd.read_csv(file, index_col='Date', parse_dates=True)
        dfs.append(df_temp)
    
    # On concatène tous les mini-DataFrames côte à côte
    # Pandas aligne intelligemment les données sur l'index (Date)
    df_final = pd.concat(dfs, axis=1)
    
    # On trie l'index de façon chronologique pour s'assurer que tout est propre
    df_final = df_final.sort_index()
    
    return df_final

def sort_ship_columns(df, start_idx=6,First_ship=0, Last_ship=None):
    """
    Réorganise les colonnes d'un dataframe à partir d'un indice donné et tronque 
    le nombre de navires conservés.
    Les colonnes avant l'indice restent intactes. 
    Les colonnes après l'indice (les navires) sont triées par ordre décroissant de leur somme.
    
    :param df: Le DataFrame d'origine
    :param start_idx: L'indice où commencent les colonnes à trier (ex: 6)
    :param end_index: Le nombre de navires triés à conserver (ex: 3 pour les 3 plus gros). 
                      Si None, tous les navires sont conservés.
    :return: Le DataFrame avec les colonnes réorganisées et tronquées
    """
    # 1. Identifier les noms des colonnes de base (les `start_idx` premières)
    base_cols = df.columns[:start_idx]
    
    # 2. Identifier les noms des colonnes des navires
    ship_cols = df.columns[start_idx:]
    
    # 3. Calculer la somme pour chaque colonne de navire
    ship_sums = df[ship_cols].sum()
    
    # 4. Obtenir les noms des navires triés par leur somme en ordre décroissant
    sorted_ship_cols = ship_sums.sort_values(ascending=False).index
    
    # 4.5 Tronquer la liste pour ne garder que le top X des navires
    if (Last_ship is not None) or (First_ship !=0):
        sorted_ship_cols = sorted_ship_cols[First_ship:Last_ship]
        
    # 5. Créer la nouvelle liste complète des colonnes (base + navires triés/tronqués)
    new_column_order = list(base_cols) + list(sorted_ship_cols)
    
    # 6. Renvoyer le dataframe réorganisé avec seulement les colonnes sélectionnées
    return df[new_column_order]



