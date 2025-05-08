import os
import re
from datetime import datetime
import pandas as pd
from rapidfuzz import process, fuzz  # Pour le fuzzy matching
from tqdm import tqdm
from collections import defaultdict
import csv

# Liste des chemins possibles pour les fichiers Netflix
file_paths = [
    '../data/raw/netflix_titles.csv',
    '../data/raw/netflix_movies_to_2025.csv',
    '../data/raw/netflix_tv_shows_to_2025.csv',
    '../data/raw/my_netflix_titles.csv'
]

def load_netflix_data():
    dfs = []
    for path in file_paths:
        if os.path.exists(path):
            print(f"Fichier Netflix trouvé : {path}")
            df_temp = pd.read_csv(path)
            dfs.append(df_temp)
    if not dfs:
        raise FileNotFoundError("Aucun fichier n'a été trouvé parmi : " + ", ".join(file_paths))
    return pd.concat(dfs, ignore_index=True)

def clean_title(title):
    """
    Nettoie le titre en supprimant tous les types de guillemets
    et en remplaçant "Partie" par "Saison".
    """
    if pd.isna(title):
        return ''
    # Supprimer les guillemets droits et typographiques
    title = re.sub(r'[\"“”]', '', title)
    # Remplacer toutes les occurrences de "Partie" par "Saison"
    title = title.replace('Partie', 'Saison')
    return title

def simplify_title(title):
    """
    Simplifie le titre pour obtenir une version utilisée lors du merge avec Netflix.
    Par exemple :
        - "Paradise Police: Saison 4: Le Jugement éternel (Épisode 10)" devient "Paradise Police"
        - "Fear Street - Saison 1 : 1994" devient "Fear Street"
    """
    if pd.isna(title):
        return ''
    title = clean_title(title)
    # Supprimer le texte entre parenthèses
    title = re.sub(r'\(.*?\)', '', title)
    # Retirer le pattern " : 1994" (ou toute année) s'il est à la fin
    title = re.sub(r'\s*:\s*\d{4}\s*$', '', title)
    # Conserver uniquement la partie avant le premier deux-points
    main = title.split(':')[0].strip()
    # Retirer " - Saison X" (pour le merge, on enlève juste cette partie)
    main = re.sub(r'\s*-\s*Saison[\s\u00A0\W]*(\d+)\s*$', '', main, flags=re.IGNORECASE)
    return main

def extract_matched_title(title):
    """
    Extrait le Matched_Title tel qu'il doit être retenu dans le dataset enrichi.
    Par exemple, à partir de :
    "2025-03-30 14:48:01,Paradise Police: Saison 4: Le Jugement éternel (Épisode 10)"
    on souhaite obtenir "Paradise Police".
    """
    if pd.isna(title):
        return ''
    title = clean_title(title)
    if ',' in title:
        title = title.split(',', 1)[1].strip()
    colon_index = title.find(':')
    if colon_index == -1:
        return title.strip()
    return title[:colon_index].strip()

def match_titles(my_title, netflix_titles, threshold=80, word_overlap_threshold=0.5):
    """
    Fonction de fuzzy matching pour comparer un titre aux titres Netflix.
    """
    if not my_title:
        return None
    normalized_title = clean_title(my_title).strip().lower()
    normalized_netflix = [clean_title(nt).strip().lower() for nt in netflix_titles]
    match, score, _ = process.extractOne(normalized_title, normalized_netflix, scorer=fuzz.token_set_ratio)
    original_words = set(normalized_title.split())
    match_words = set(match.split())
    if len(original_words) == 0:
        return my_title
    overlap_ratio = len(original_words.intersection(match_words)) / len(original_words)
    if score < threshold or overlap_ratio < word_overlap_threshold:
        return my_title
    return match

def categorize_title(title, title_counts):
    """
    Détermine le type de contenu (TV Show ou Movie).
    Le titre est d'abord nettoyé pour convertir "Partie X" en "Saison X",
    ce qui aide à identifier correctement les séries.
    """
    if pd.isna(title):
        return ''
    title_clean = clean_title(title)
    if re.search(r'(saison|season|épisode|episode|mini-épisode|mini-série|pilot)', title_clean, re.IGNORECASE):
        return "TV Show"
    return "Movie"

def extract_season(title):
    """
    Extrait le numéro de saison à partir du titre.
    Par exemple, "Paradise Police: Saison 2: ..." renverra 2.
    """
    if pd.isna(title):
        return None
    title_clean = clean_title(title)
    match = re.search(r'(Saison|Season)\s*(\d+)', title_clean, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return None

def main():
    print("🔄 Chargement des données...")
    # Charger le fichier d'activité et nettoyer les titres
    my_history = pd.read_csv('../data/raw/ViewingActivity.csv')
    my_history['Title'] = my_history['Title'].apply(clean_title)

    # Charger les données Netflix et nettoyer les titres
    netflix_df = load_netflix_data()
    netflix_df['title'] = netflix_df['title'].apply(clean_title)
    # Supprimer les enregistrements sans titre
    my_history = my_history.dropna(subset=['Title'])
    
    # Créer la colonne Matched_Title à partir de la portion désirée du titre
    my_history['Matched_Title'] = my_history['Title'].apply(extract_matched_title)
    
    # Créer la colonne simplifiée dans netflix_df pour le merge
    netflix_df['simplified_title'] = netflix_df['title'].apply(simplify_title)
    netflix_titles_list = netflix_df['simplified_title'].tolist()

    print("🚀 Fusion des données...")
    merged_df = pd.merge(
        my_history, netflix_df,
        left_on='Matched_Title', right_on='simplified_title',
        how='left', suffixes=('_history', '_netflix')
    )

    title_counts = defaultdict(int)
    for t in merged_df['Title']:
        main_title = t.split(':')[0].strip()
        title_counts[main_title] += 1

    merged_df['corrected_type'] = merged_df['Title'].apply(lambda x: categorize_title(x, title_counts))
    print("Colonnes existantes après fusion :", merged_df.columns.tolist())

    enriched_df = merged_df[['Start Time', 'Title', 'Matched_Title', 'corrected_type',
                                'director', 'country', 'listed_in', 'duration',
                                'rating', 'release_year']].copy()
    enriched_df.rename(columns={'Start Time': 'Date Watched'}, inplace=True)

    required_cols = ['Title', 'Date Watched', 'corrected_type']
    missing_data = enriched_df[enriched_df[required_cols].isna().any(axis=1)]
    print(f"⚠️ Missing minimal data (Title, Date Watched, corrected_type): {len(missing_data)} records")

    enriched_df = enriched_df.dropna(subset=required_cols)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    enriched_output_path = f"../data/processed/enriched_netflix_history_{timestamp}.csv"
    
    # Enregistrer le fichier sans guillemets grâce à quoting=csv.QUOTE_NONE et escapechar
    enriched_df.to_csv(enriched_output_path, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    print(f"✅ Fichier enriched sauvegardé dans : {enriched_output_path}")

    if not missing_data.empty:
        debug_output_path = f"../data/processed/debug_unmatched_titles_{timestamp}.csv"
        missing_data.to_csv(debug_output_path, index=False)
        print(f"✅ Fichier des titres incomplets sauvegardé dans : {debug_output_path}")
    else:
        print("Aucune donnée manquante, le fichier debug n'a pas été sauvegardé.")

    print("✅ Data cleaning and merging completed successfully!")

if __name__ == "__main__":
    main()
