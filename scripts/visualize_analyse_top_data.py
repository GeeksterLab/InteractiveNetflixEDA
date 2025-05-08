import os
import glob
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Définition du chemin de sauvegarde des visualisations
save_path = "/Users/shaina/Desktop/My_projects/APP/Interactif_Netflix_EDA/visualization/"
os.makedirs(save_path, exist_ok=True)

# Fonction pour sauvegarder les visualisations
def save_visualization(title):
    filename = title.replace(" ", "_").replace(":", "").lower() + ".png"
    plt.savefig(os.path.join(save_path, filename), bbox_inches="tight")
    plt.close()  # Fermer la figure pour libérer la mémoire
    print(f"✅ Graphique sauvegardé : {filename}")

# Set style for visuals
sns.set_theme(style="darkgrid")

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

# Convertir "Date Watched" en datetime
# df['Date Watched'] = pd.to_datetime(df['Date Watched'], errors='coerce')
df['Date Watched'] = pd.to_datetime(df['Date Watched'], format='%Y-%m-%d %H:%M:%S', errors='coerce')


# Séparer les films et les séries
movies = df[df['corrected_type'] == 'Movie']
series = df[df['corrected_type'] == 'TV Show']

# 🔹 Top 20 des séries les plus regardées
top_series = series['Title'].value_counts().head(20)
plt.figure(figsize=(12,6))
top_series.plot(kind='bar', color='blue')
title = 'Top 20 Most Watched TV Shows'
plt.title(title)
plt.xlabel('TV Show Title')
plt.ylabel('Number of Views')
plt.xticks(rotation=90)
save_visualization(title)

# 🔹 Top 20 des films les plus regardés
top_movies = movies['Title'].value_counts().head(20)
plt.figure(figsize=(12,6))
top_movies.plot(kind='bar', color='green')
title = 'Top 20 Most Watched Movies'
plt.title(title)
plt.xlabel('Movie Title')
plt.ylabel('Number of Views')
plt.xticks(rotation=90)
save_visualization(title)

# 🔹 Top 10 des séries et films regardés par année
df['Year Watched'] = df['Date Watched'].dt.year
for year in range(2016, 2026):  # De 2016 à 2025
    yearly_data = df[df['Year Watched'] == year]
    if not yearly_data.empty:
        top_yearly = yearly_data['Title'].value_counts().head(10)
        plt.figure(figsize=(12,6))
        top_yearly.plot(kind='bar', color='purple')
        title = f'Top 10 Most Watched Titles in {year}'
        plt.title(title)
        plt.xlabel('Title')
        plt.ylabel('Number of Views')
        plt.xticks(rotation=90)
        save_visualization(title)

# 🔹 Top 10 des séries et films regardés par mois
df['Month Watched'] = df['Date Watched'].dt.to_period('M')
for month in df['Month Watched'].unique():
    monthly_data = df[df['Month Watched'] == month]
    if not monthly_data.empty:
        top_monthly = monthly_data['Title'].value_counts().head(10)
        plt.figure(figsize=(12,6))
        top_monthly.plot(kind='bar', color='red')
        title = f'Top 10 Most Watched Titles in {month}'
        plt.title(title)
        plt.xlabel('Title')
        plt.ylabel('Number of Views')
        plt.xticks(rotation=90)
        save_visualization(title)
