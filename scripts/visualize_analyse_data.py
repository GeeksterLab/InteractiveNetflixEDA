# # scripts/visualize_analyse_data.py

# import os
# import glob
# import re
# from datetime import datetime
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Définition du chemin de sauvegarde des visualisations
# save_path = "/Users/shaina/Desktop/My_projects/APP/Netflix_EDA/visualization/"


# # Fonction pour sauvegarder les visualisations avec un nom basé sur le titre
# def save_visualization(title):
#     filename = title.replace(" ", "_").replace(":", "").lower() + ".png"
#     plt.savefig(os.path.join(save_path, filename), bbox_inches="tight")
#     plt.close()  # Fermer la figure après sauvegarde
#     print(f"✅ Graphique sauvegardé : {filename}")

# # Set style for visuals
# sns.set_theme(style="darkgrid")

# # --- Sélection dynamique du fichier enrichi ---
# directory = "data/processed/"
# files = glob.glob(os.path.join(directory, "enriched_netflix_history_*.csv"))
# pattern = r"enriched_netflix_history_(\d{8}_\d{6})\.csv"
# file_dates = []
# for f in files:
#     basename = os.path.basename(f)
#     match = re.search(pattern, basename)
#     if match:
#         date_str = match.group(1)
#         file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
#         file_dates.append((f, file_date))

# if not file_dates:
#     raise FileNotFoundError("Aucun fichier enriched_netflix_history trouvé dans le dossier.")

# now = datetime.now()
# closest_file, closest_date = min(file_dates, key=lambda x: abs(now - x[1]))
# print(f"Chargement du fichier : {closest_file} (date extraite : {closest_date})")
# df = pd.read_csv(closest_file)
# # --- Fin de la sélection dynamique ---

# # Inspect data
# print(df.head())

# # Convert "Date Watched" to datetime
# # df['Date Watched'] = pd.to_datetime(df['Date Watched'], format='%m/%d/%y')
# df['Date Watched'] = pd.to_datetime(df['Date Watched'], format='%Y-%m-%d %H:%M:%S', errors='coerce')


# # Resample à la fin de chaque mois
# monthly_views = df.resample('M', on='Date Watched').size()

# plt.figure(figsize=(12,6))
# monthly_views.plot(kind='bar', color='skyblue')

# title = 'Monthly Netflix Viewing Frequency'
# plt.title(title)
# plt.xlabel('Month')
# plt.ylabel('Number of Views')

# # Affiche les mois tous les 3 mois
# plt.xticks(range(0, len(monthly_views.index), 3),
#             monthly_views.index.strftime('%Y-%m')[::3],
#             rotation=45)

# plt.tight_layout()
# save_visualization(title)
# # plt.show()

# # Ce graphique montre le nombre de films/séries que j'ai regardés sur Netflix depuis 2016, et la fréquence.
# # Chaque barre représente clairement un mois précis entre 2016 et 2025.
# # La hauteur des barres indique précisément le nombre de vidéos que tu as visionnées chaque mois, sur une échelle allant d'environ 0 à 160 vidéos maximum (en fonction du mois où tu as le plus visionné


# # --- Analyse de la durée des films ---
# movies = df[df['corrected_type'] == 'Movie'].copy()
# movies['duration_minutes'] = pd.to_numeric(
#     movies['duration'].str.replace(' min','', regex=False),
#     errors='coerce'
# )
# movies.dropna(subset=['duration_minutes'], inplace=True)

# plt.figure(figsize=(10,5))
# sns.histplot(movies['duration_minutes'], bins=20, kde=True)
# title = 'Distribution of Movie Durations Watched'
# plt.xlabel('Duration (minutes)')
# plt.ylabel('Count')
# save_visualization(title)
# # plt.show()

# # Ce graphique montre la durée en minutes des films que j'ai regardés sur Netflix depuis 2016, et le nombre de films visionnés pour chaque durée.
# # Les barres montrent précisément le nombre exact de films regardés pour chaque durée.
# #La courbe représente clairement la tendance générale de la répartition, facilitant l'identification rapide des durées que tu regardes le plus souvent.


# # --- Habitudes hebdomadaires ---
# df['Day_of_Week'] = df['Date Watched'].dt.day_name()
# weekly_counts = df['Day_of_Week'].value_counts().reindex(
#     ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# )
# plt.figure(figsize=(10,6))
# sns.barplot(x=weekly_counts.index, y=weekly_counts.values)
# title = "Netflix Watching Frequency by Day of Week"
# plt.xlabel("Day of Week")
# plt.ylabel("Number of Views")
# save_visualization(title)
# # plt.show()

# # Ce graphique représente clairement le nombre total de films ou séries visionnés selon chaque jour de la semaine (de lundi à dimanche), pour toute ta période d'observation (2016 à 2025).
# # L'axe horizontal (Day of Week) affiche chaque jour de la semaine.
# # L'axe vertical (Number of Views) indique précisément le nombre total de vidéos vues par jour de la semaine.


# # --- Fréquence annuelle ---
# df['Year Watched'] = df['Date Watched'].dt.year
# yearly_views = df['Year Watched'].value_counts().sort_index()
# plt.figure(figsize=(8,5))
# yearly_views.plot(kind='line', marker='o')
# title = 'Netflix Viewing Trends by Year'
# plt.ylabel('Number of Views')
# plt.xlabel('Year')
# plt.tight_layout()
# save_visualization(title)
# # plt.show()

# # L'axe horizontal (Year) affiche chaque année observée.
# # L'axe vertical (Number of Views) indique le nombre total de vidéos regardées par an (entre 0 et environ 350 vidéos par année).


# # --- Corrélation entre l'année de sortie du contenu et l'année de visionnage ---
# plt.figure(figsize=(10,6))
# sns.scatterplot(data=df, x='release_year', y='Year Watched')
# title = 'Relation between Content Release Year and Watching Year'
# plt.xlabel('Content Release Year')
# plt.ylabel('Year Watched')
# save_visualization(title)
# # plt.show()

# # Ce graphique (nuage de points) montre la relation entre l'année de sortie du contenu (axe horizontal : Content Release Year) et l'année où tu l'as regardé (axe vertical : Year Watched).



# scripts/visualize_analyse_data.py

import os
import glob
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
# Définition du chemin de sauvegarde des visualisations
save_path = "/Users/shaina/Desktop/My_projects/APP/Interactif_Netflix_EDA/visualization/"

# Style seaborn
sns.set_theme(style="darkgrid")


# --- Helpers ---

def save_visualization(title: str):
    """
    Sauvegarde la figure matplotlib courante sous un nom déterminé à partir du titre.
    """
    filename = title.replace(" ", "_").replace(":", "").lower() + ".png"
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, filename), bbox_inches="tight")
    plt.close()
    print(f"✅ Graphique sauvegardé : {filename}")


def select_enriched_file() -> pd.DataFrame:
    """
    Parcourt data/processed/, choisit le fichier le plus récent au plus proche de maintenant,
    et renvoie le DataFrame lu.
    """
    directory = "data/processed/"
    pattern = r"enriched_netflix_history_(\d{8}_\d{6})\.csv"
    candidates = []
    for f in glob.glob(os.path.join(directory, "enriched_netflix_history_*.csv")):
        m = re.search(pattern, os.path.basename(f))
        if m:
            dt = datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
            candidates.append((f, dt))
    if not candidates:
        raise FileNotFoundError("Aucun fichier enriched_netflix_history trouvé dans le dossier.")
    # on choisit celui dont la date est la plus proche de now
    closest_file, _ = min(candidates, key=lambda x: abs(datetime.now() - x[1]))
    print(f"Chargement du fichier : {closest_file}")
    return pd.read_csv(closest_file)


# --- Les différents graphiques ---

def plot_monthly_views(df: pd.DataFrame):
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    monthly = df.resample("M", on="Date Watched").size()
    plt.figure(figsize=(12, 6))
    monthly.plot(kind="bar", color="skyblue")
    title = "Monthly Netflix Viewing Frequency"
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel("Number of Views")
    plt.xticks(
        range(0, len(monthly), 3),
        monthly.index.strftime("%Y-%m")[::3],
        rotation=45,
    )
    plt.tight_layout()
    save_visualization(title)


def plot_movie_duration(df: pd.DataFrame):
    movies = df[df["corrected_type"] == "Movie"].copy()
    movies["duration_minutes"] = pd.to_numeric(
        movies["duration"].str.replace(" min", "", regex=False), errors="coerce"
    )
    movies.dropna(subset=["duration_minutes"], inplace=True)
    plt.figure(figsize=(10, 5))
    sns.histplot(movies["duration_minutes"], bins=20, kde=True)
    title = "Distribution of Movie Durations Watched"
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Count")
    save_visualization(title)


def plot_weekly_habits(df: pd.DataFrame):
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    df["day"] = df["Date Watched"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = df["day"].value_counts().reindex(order)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=counts.index, y=counts.values)
    title = "Netflix Watching Frequency by Day of Week"
    plt.xlabel("Day of Week")
    plt.ylabel("Number of Views")
    save_visualization(title)


def plot_yearly_trends(df: pd.DataFrame):
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    df["year"] = df["Date Watched"].dt.year
    counts = df["year"].value_counts().sort_index()
    plt.figure(figsize=(8, 5))
    counts.plot(kind="line", marker="o")
    title = "Netflix Viewing Trends by Year"
    plt.xlabel("Year")
    plt.ylabel("Number of Views")
    plt.tight_layout()
    save_visualization(title)


def plot_release_vs_watch(df: pd.DataFrame):
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="release_year", y=df["Date Watched"].dt.year)
    title = "Relation between Content Release Year and Watching Year"
    plt.xlabel("Content Release Year")
    plt.ylabel("Year Watched")
    save_visualization(title)


# Dictionnaire permettant d’itérer sur tous les tracés
PLOT_FUNCS = [
    plot_monthly_views,
    plot_movie_duration,
    plot_weekly_habits,
    plot_yearly_trends,
    plot_release_vs_watch,
]


# --- Point d’entrée ---

def main():
    df = select_enriched_file()
    for fn in PLOT_FUNCS:
        fn(df)


if __name__ == "__main__":
    main()
