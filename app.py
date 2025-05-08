# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import glob
from datetime import datetime

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/css/style.css")

# Définir le symbole d'animation
animation_symbol = "❄"

# Combiner le HTML et le CSS dans une seule chaîne
html_css = f"""
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>
<div class="snowflake">{animation_symbol}</div>

<style>
/* Animation pour un fond dynamique en dégradé */
@keyframes gradientAnimation {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}

/* Appliquer l'animation sur le body */
body {{
    background: linear-gradient(270deg, #121212, #00E676, #121212);
    background-size: 600% 600%;
    animation: gradientAnimation 15s ease infinite;
    font-family: 'Roboto', sans-serif;
}}

/* Sidebar avec un fond légèrement contrasté */
.sidebar .sidebar-content {{
    # background: #1E1E1E;
}}

/* Titres avec une couleur néon */
h1, h2, h3, h4, h5, h6 {{
    color: #00E676;
}}

/* Boutons et éléments interactifs */
.stButton > button {{
    background-color: #00E176;
    color: #121212;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}}
.stButton > button:hover {{
    background-color: #00C853;
}}

/* Cartes et conteneurs avec une ombre légère */
.css-1d391kg, .css-1ekf893 {{
    background: #1E1E1E;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    padding: 10px;
}}

/* Personnalisation des barres de défilement */
::-webkit-scrollbar {{
    width: 8px;
}}
::-webkit-scrollbar-track {{
    background: #1E1E1E;
}}
::-webkit-scrollbar-thumb {{
    background-color: #00E676;
    border-radius: 10px;
}}
</style>
"""

st.markdown(html_css, unsafe_allow_html=True)


# --- Sélection dynamique du fichier enrichi ---
def select_enriched_file():
    """Sélectionne le fichier enriched_netflix_history dont la date est la plus proche d'aujourd'hui."""
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
    return closest_file

# Chargement des données avec st.cache_data
@st.cache_data
def load_data():
    enriched_file = select_enriched_file()
    df = pd.read_csv(enriched_file)
    return df

# Charger et préparer les données
df = load_data()
# Conversion de "Date Watched" en datetime avec le format spécifié
# df["Date Watched"] = pd.to_datetime(df["Date Watched"], format="%m/%d/%y", errors="coerce")
df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")

# ------------------ PARTIE VISUALISATIONS DYNAMIQUES ------------------

# Fonction 1 : Relation entre l'année de sortie et l'année de visionnage
def get_correlation_figure(df):
    df = df.copy()
    df["watch_year"] = df["Date Watched"].dt.year
    fig = px.scatter(
        df,
        x="release_year",
        y="watch_year",
        title="Relation entre l'année de sortie et l'année de visionnage",
        labels={"release_year": "Année de sortie", "watch_year": "Année de visionnage"}
    )
    return fig

# Fonction 2 : Fréquence des visionnages selon les jours de la semaine
def get_frequency_day_figure(df):
    df = df.copy()
    df["day_of_week"] = df["Date Watched"].dt.day_name()
    freq = df["day_of_week"].value_counts().reset_index()
    freq.columns = ["day_of_week", "count"]
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    freq["day_of_week"] = pd.Categorical(freq["day_of_week"], categories=order, ordered=True)
    freq = freq.sort_values("day_of_week")
    fig = px.bar(
        freq,
        x="day_of_week",
        y="count",
        title="Fréquence des visionnages selon les jours de la semaine",
        labels={"day_of_week": "Jour de la semaine", "count": "Nombre de visionnages"}
    )
    return fig

# Fonction 3 : Fréquence des visionnages selon les mois
def get_frequency_month_figure(df):
    df = df.copy()
    df["month"] = df["Date Watched"].dt.month_name()
    freq = df["month"].value_counts().reset_index()
    freq.columns = ["month", "count"]
    mois = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]
    freq["month"] = pd.Categorical(freq["month"], categories=mois, ordered=True)
    freq = freq.sort_values("month")
    fig = px.bar(
        freq,
        x="month",
        y="count",
        title="Fréquence des visionnages selon les mois",
        labels={"month": "Mois", "count": "Nombre de visionnages"}
    )
    return fig

# Fonction 4 : Fréquence des visionnages par année
def get_frequency_year_figure(df):
    df = df.copy()
    df["watch_year"] = df["Date Watched"].dt.year
    freq = df["watch_year"].value_counts().reset_index()
    freq.columns = ["watch_year", "count"]
    freq = freq.sort_values("watch_year")
    fig = px.bar(
        freq,
        x="watch_year",
        y="count",
        title="Fréquence des visionnages par année",
        labels={"watch_year": "Année", "count": "Nombre de visionnages"}
    )
    return fig

# Fonction 5 : Distribution des durées des films regardés
def get_movie_duration_figure(df):
    df = df.copy()
    df["duration_min"] = pd.to_numeric(df["duration"].str.extract(r"(\d+)")[0], errors="coerce")
    fig = px.histogram(
        df,
        x="duration_min",
        nbins=30,
        title="Distribution des durées des films regardés",
        labels={"duration_min": "Durée (minutes)"}
    )
    return fig

# Fonction 6 : Top 20 des films les plus regardés
def get_top_20_movies_figure(df):
    df = df.copy()
    movies = df[df["corrected_type"] == "Movie"]
    top_movies = movies["Title"].value_counts().nlargest(20).reset_index()
    top_movies.columns = ["Title", "count"]
    fig = px.bar(
        top_movies,
        x="Title",
        y="count",
        title="Top 20 des films les plus regardés",
        labels={"Title": "Film", "count": "Nombre de visionnages"}
    )
    return fig

# Fonction 7 : Top 20 des séries les plus regardées
def get_top_20_tv_shows_figure(df):
    df = df.copy()
    tv_shows = df[df["corrected_type"] == "TV Show"]
    top_tv = tv_shows["Matched_Title"].value_counts().nlargest(20).reset_index()
    top_tv.columns = ["Matched_Title", "count"]
    fig = px.bar(
        top_tv,
        x="Matched_Title",
        y="count",
        title="Top 20 des séries les plus regardées",
        labels={"Matched_Title": "Série", "count": "Nombre de visionnages"}
    )
    return fig

# Dictionnaire pour visualisations dynamiques
visualizations = {
    "Année de sortie et année de visionnage": get_correlation_figure,
    "Fréquence selon les jours de la semaine": get_frequency_day_figure,
    "Fréquence selon les mois": get_frequency_month_figure,
    "Fréquence par année": get_frequency_year_figure,
    "Durée des films regardés": get_movie_duration_figure,
    "Top 20 des films les plus regardés": get_top_20_movies_figure,
    "Top 20 des séries les plus regardées": get_top_20_tv_shows_figure
}

# ------------------ SECTION D'EXPLORATION PAR TITRE ------------------

def extract_season(title):
    """
    Extrait le numéro de saison depuis le titre.
    Cherche "Saison X" ou "Season X" et renvoie X comme entier.
    """
    match = re.search(r'(Saison|Season)\s*(\d+)', title, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return None

def extract_episode(title):
    """
    Extrait les informations d'épisode depuis le titre.
    Par exemple, pour "Nom du show : Saison 3 : Episode 5",
    renvoie "Episode 5" ou "Saison 3 : Episode 5" selon le besoin.
    Ici, on renvoie tout ce qui vient après la mention de la saison.
    """
    match = re.search(r'(Saison|Season)\s*\d+\s*:\s*(.+)', title, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return ""

def display_title_details(df, content_type):
    st.header("Détail par titre")
    
    # Filtrer selon le type de contenu
    if "corrected_type" in df.columns:
        if content_type == "Movies":
            df_type = df[df["corrected_type"] == "Movie"]
        else:
            df_type = df[df["corrected_type"] == "TV Show"]
    else:
        df_type = df

    # Sélection du titre
    titles = sorted(df_type["Matched_Title"].dropna().unique())
    selected_title = st.selectbox("Sélectionnez un titre :", titles)
    df_title = df_type[df_type["Matched_Title"] == selected_title]

    # Nombre de visionnages
    num_viewings = df_title.shape[0]
    st.write(f"**Nombre total de visionnages pour _{selected_title}_ : {num_viewings}**")

    # Pour les TV Shows, on calcule les détails par épisode
    if content_type == "TV Shows":
        st.write("### Détails par épisode")
        # Copie du DataFrame pour éviter des modifications inattendues
        df_title = df_title.copy()
        # Extraire la saison et les informations d'épisode depuis le titre
        df_title["Season"] = df_title["Title"].apply(extract_season)
        df_title["Episode Info"] = df_title["Title"].apply(extract_episode)
        # Récupérer la liste des saisons disponibles
        seasons = sorted(df_title["Season"].dropna().unique())
        if len(seasons) > 0:
            selected_season = st.selectbox("Sélectionnez une saison :", seasons)
            df_season = df_title[df_title["Season"] == selected_season]
            # Calculer le nombre de visionnages par épisode
            episode_counts = df_season.groupby("Episode Info").size().reset_index(name="Nombre de visionnages")
            if not episode_counts.empty:
                # Extraire le numéro d'épisode pour trier
                episode_counts["Episode_Number"] = episode_counts["Episode Info"].apply(
                    lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else None
                )
                # Trier par numéro d'épisode (du plus petit au plus grand)
                episode_counts = episode_counts.sort_values(by="Episode_Number")
                # Réindexer pour un affichage propre et supprimer la colonne temporaire
                episode_counts = episode_counts.reset_index(drop=True).drop(columns=["Episode_Number"])
                st.dataframe(episode_counts)
            else:
                st.write("Aucune information détaillée d'épisode n'a pu être extraite pour cette saison.")
        else:
            st.write("Aucune information de saison n'a été trouvée pour ce titre.")


# ------------------ INTERFACE PRINCIPALE ------------------

st.title("Interactif Netflix EDA ")
st.write("Choisissez dans la barre latérale la section à afficher.")

# Menu principal dans la sidebar pour choisir la section
section = st.sidebar.radio("Sélectionnez une section :", ["Visualisations", "Exploration par titre"])

if section == "Visualisations":
    st.header("Visualisations dynamiques")
    option = st.sidebar.selectbox("Sélectionnez une visualisation :", list(visualizations.keys()))
    fig = visualizations[option](df)
    st.header(option)
    st.plotly_chart(fig, use_container_width=True)

elif section == "Exploration par titre":
    st.header("Exploration par titre")
    content_type = st.sidebar.radio("Choisissez le type de contenu :", ["Movies", "TV Shows"])
    display_title_details(df, content_type)
