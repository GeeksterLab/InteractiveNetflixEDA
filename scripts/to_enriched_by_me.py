# import pandas as pd

# def main():
#     # Charger le fichier enrichi
#     # df = pd.read_csv("data/processed/enriched_netflix_history_20250405_120727.csv")
    
#     # --- Sélection dynamique du fichier enrichi ---
#     directory = "data/processed/"
#     files = glob.glob(os.path.join(directory, "enriched_netflix_history_*.csv"))
#     pattern = r"enriched_netflix_history_(\d{8}_\d{6})\.csv"
#     file_dates = []
#     for f in files:
#         basename = os.path.basename(f)
#         match = re.search(pattern, basename)
#         if match:
#             date_str = match.group(1)
#             file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
#             file_dates.append((f, file_date))

#     if not file_dates:
#         raise FileNotFoundError("Aucun fichier enriched_netflix_history trouvé dans le dossier.")

# now = datetime.now()
# closest_file, closest_date = min(file_dates, key=lambda x: abs(now - x[1]))
# print(f"Chargement du fichier : {closest_file} (date extraite : {closest_date})")
# df = pd.read_csv(closest_file)
# # --- Fin de la sélection dynamique ---

#     # Vérifier les colonnes attendues (adaptation possible selon ton CSV)
#     expected_columns = ['Title', 'Matched_Title', 'corrected_type', 'director', 'country', 'listed_in', 'duration', 'rating', 'release_year', 'Date Watched']
#     print("Colonnes présentes :", df.columns.tolist())
    
#     # On considère comme "incomplet" les lignes où toutes les colonnes d'information (autres que Title et corrected_type) sont manquantes.
#     optional_cols = ['Matched_Title', 'director', 'country', 'listed_in', 'duration', 'rating', 'release_year']
    
#     # On filtre les lignes dont tous ces champs sont NaN et dont corrected_type est soit "TV Show" soit "Movie"
#     df_incomplete = df[df[optional_cols].isna().all(axis=1) & df['corrected_type'].isin(["TV Show", "Movie"])]
    
#     print(f"Nombre de lignes incomplètes détectées : {len(df_incomplete)}")
#     print(df_incomplete[['Title', 'corrected_type']].head(10))
    

#     # Générer un timestamp pour créer des noms de fichiers uniques
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     # Sauvegarder les lignes incomplètes dans un CSV pour les enrichir ultérieurement
#     output_file = f:"data/processed/incomplete_titles_custom_{timestamp}csv"
#     df_incomplete.to_csv(output_file, index=False)
#     print(f"✅ Fichier des lignes incomplètes sauvegardé dans : {output_file}")

# if __name__ == "__main__":
#     main()

import os
import glob
import re
from datetime import datetime
import pandas as pd

def main():
    # --- Sélection dynamique du fichier enrichi ---
    directory = "data/processed/"
    files = glob.glob(os.path.join(directory, "enriched_netflix_history_*.csv"))
    pattern = r"enriched_netflix_history_(\d{8}_\d{6})\.csv"
    file_dates = []
    for f in files:
        basename = os.path.basename(f)
        match = re.search(pattern, basename)
        if match:
            date_str = match.group(1)
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            file_dates.append((f, file_date))

    if not file_dates:
        raise FileNotFoundError("Aucun fichier enriched_netflix_history trouvé dans le dossier.")

    now = datetime.now()
    closest_file, closest_date = min(file_dates, key=lambda x: abs(now - x[1]))
    print(f"Chargement du fichier : {closest_file} (date extraite : {closest_date})")
    df = pd.read_csv(closest_file)
    # --- Fin de la sélection dynamique ---

    # Vérifier les colonnes attendues (adaptation possible selon ton CSV)
    expected_columns = [
        'Title', 'Matched_Title', 'corrected_type', 'director', 'country',
        'listed_in', 'duration', 'rating', 'release_year', 'Date Watched'
    ]
    print("Colonnes présentes :", df.columns.tolist())

    # On considère comme "incomplet" les lignes où toutes les colonnes d'information
    # (autres que Title et corrected_type) sont manquantes.
    optional_cols = [
        'Matched_Title', 'director', 'country',
        'listed_in', 'duration', 'rating', 'release_year'
    ]

    # On filtre les lignes dont tous ces champs sont NaN
    # ET dont corrected_type est "TV Show" ou "Movie"
    df_incomplete = df[
        df[optional_cols].isna().all(axis=1)
        & df['corrected_type'].isin(["TV Show", "Movie"])
    ]

    print(f"Nombre de lignes incomplètes détectées : {len(df_incomplete)}")
    print(df_incomplete[['Title', 'corrected_type']].head(10))

    # Générer un timestamp pour créer des noms de fichiers uniques
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sauvegarder les lignes incomplètes dans un CSV
    output_file = f"data/processed/incomplete_titles_custom_{timestamp}.csv"
    df_incomplete.to_csv(output_file, index=False)
    print(f"✅ Fichier des lignes incomplètes sauvegardé dans : {output_file}")

if __name__ == "__main__":
    main()
