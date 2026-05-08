"""Generate a PDF report from existing visualization files."""

from __future__ import annotations

from datetime import datetime

from fpdf import FPDF

from netflix_utils import REPORTS_DIR, VISUALIZATION_DIR, safe_filename

STATIC_GRAPHS = {
    "Relation between Content Release Year and Watching Year": "Relation entre l'année de sortie et l'année de visionnage.",
    "Netflix Watching Frequency by Day of Week": "Fréquence des visionnages selon les jours de la semaine.",
    "Monthly Netflix Viewing Frequency": "Fréquence des visionnages selon les mois.",
    "Netflix Viewing Trends by Year": "Fréquence des visionnages par année.",
    "Distribution of Movie Durations Watched": "Distribution des durées des films regardés.",
    "Top 20 Most Watched Movies": "Top 20 des films les plus regardés.",
    "Top 20 Most Watched TV Shows": "Top 20 des séries les plus regardées.",
}


def collect_graphs() -> list[tuple[str, str]]:
    graphs: list[tuple[str, str]] = []

    for title, description in STATIC_GRAPHS.items():
        filename = safe_filename(title)
        if (VISUALIZATION_DIR / filename).exists():
            graphs.append((filename, description))
        else:
            print(f"⚠️ Missing chart: {filename}")

    for graph_path in sorted(VISUALIZATION_DIR.glob("top_10_most_watched_titles_in_*.png")):
        readable = graph_path.stem.replace("top_10_most_watched_titles_in_", "")
        graphs.append((graph_path.name, f"Top 10 des titres les plus regardés sur la période {readable}."))

    return graphs


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"Netflix_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, "Netflix Viewing Analysis Report", ln=True, align="C")
    pdf.ln(10)

    graphs = collect_graphs()
    if not graphs:
        print("⚠️ No visualization found. Run visualize scripts first.")

    for filename, description in graphs:
        graph_path = VISUALIZATION_DIR / filename
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 10, description, align="C")
        pdf.ln(5)
        pdf.image(str(graph_path), x=10, w=180)

    pdf.output(str(report_path))
    print(f"✅ PDF report generated: {report_path}")


if __name__ == "__main__":
    main()
