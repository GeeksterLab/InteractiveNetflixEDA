from fpdf import FPDF
import os
from datetime import datetime

# Dossier où sera sauvegardé le PDF
report_folder = "reports"
# os.makedirs(report_folder, exist_ok=True)  # Crée le dossier s'il n'existe pas

# Génération d'un nom de fichier unique avec date et heure
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
report_filename = f"Netflix_Analysis_Report_{timestamp}.pdf"
report_path = os.path.join(report_folder, report_filename)

visualization_path = "visualization/"

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Page de titre
pdf.add_page()
pdf.set_font("Arial", style='B', size=16)
pdf.cell(200, 10, "Netflix Viewing Analysis Report", ln=True, align='C')
pdf.ln(10)

# Liste des visualisations et leur description
graphs = {
    "Correlation between Content Release Year and Watching Year.png": "Relation entre l'année de sortie et l'année de visionnage.",
    "Frequency by Day of Week.png": "Fréquence des visionnages selon les jours de la semaine.",
    "Frequency by Month.png": "Fréquence des visionnages selon les mois.",
    "Frequency by Year.png": "Fréquence des visionnages par année.",
    "Movie Duration Watching.png": "Distribution des durées des films regardés.",
    "top_20_most_watched_movies.png": "Top 20 des films les plus regardés.",
    "top_20_most_watched_tv_shows.png": "Top 20 des séries les plus regardées.",
}

# # Ajout des visualisations annuelles
# for year in range(2016, 2026):
#     graphs[f"top_10_most_watched_titles_in_{year}.png"] = f"Top 10 des titres les plus regardés en {year}."
for year in range(2016, 2026):
    filename = f"top_10_most_watched_titles_in_{year}.png"
    graph_path = os.path.join(visualization_path, filename)
    if os.path.exists(graph_path):
        graphs[filename] = f"Top 10 des titres les plus regardés en {year}."


# Ajout des visualisations mensuelles
for year in range(2016, 2026):
    for month in range(1, 13):
        month_str = f"{year}-{month:02d}"
        filename = f"top_10_most_watched_titles_in_{month_str}.png"
        graph_path = os.path.join(visualization_path, filename)
        if os.path.exists(graph_path):
            graphs[filename] = f"Top 10 des titres les plus regardés en {month_str}."

# Ajout des images au rapport
for graph, description in graphs.items():
    graph_path = os.path.join(visualization_path, graph)
    if os.path.exists(graph_path):
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, description, ln=True, align='C')
        pdf.ln(5)
        pdf.image(graph_path, x=10, w=180)
    else:
        print(f"⚠️ Fichier introuvable: {graph}")

# Sauvegarde du rapport PDF
pdf.output(report_path)
print(f"✅ Rapport PDF généré avec succès : {report_path}")
