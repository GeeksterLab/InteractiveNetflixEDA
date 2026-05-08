
# 🎥 Netflix EDA

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://interactivenetflixeda.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)

---

## 📖 Table of Contents

1.  [Project Overview](#-project-overview)
2.  [Project Structure](#-project-structure)
3.  [Key Features](#-key-features)
4.  [Libraries](#-libraries)
5.  [Tech Stack](#-tech-stack)
6.  [Installation & Run](#-installation--run)
7.  [Streamlit Interface](#-streamlit-interface)
8. [Tests & Coverage](#-tests--coverage)
9. [License](#-license)
10. [Auteur](#-auteur)

---

## 🎯 Project Overview

Netflix EDA is a complete data pipeline and interactive dashboard designed to analyze real Netflix viewing history.

This project focuses on transforming noisy real-world data into a clean, structured, and analyzable dataset.

It demonstrates:

- Real-world data cleaning challenges (noisy titles, technical assets)
- Title normalization and catalog matching
- Feature extraction (TV shows, seasons, episodes)
- Visualization and reporting
- Interactive exploration via Streamlit

The goal is to showcase **data engineering + EDA + product thinking** in a single project.

---

## 📂 Project Structure

```
InteractiveNetflixEDA/
├── app/ # Streamlit dashboard
├── assets/ # CSS & UI elements
├── data/
│ ├── raw/ # Original Netflix data
│ └── processed/ # Cleaned datasets
├── scripts/ # Data pipeline (cleaning, merge, reports)
├── visualization/ # Generated charts
├── reports/ # PDF reports
├── tests/ # Unit tests
├── Makefile # Project commands
└── README.md
```

## 🎯 Key Features

- Robust cleaning of noisy Netflix data
- Detection and removal of technical assets (hooks, trailers, clips)
- Title normalization and matching with catalog metadata
- Extraction of TV show structure (seasons & episodes)
- Automated visualization pipeline
- PDF report generation
- Interactive Streamlit dashboard

---

## 📦 Libraries

* **pandas** → Data management and analysis.
* **matplotlib** → Data visualization.
* **seaborn** → Advanced data visualization.
* **numpy** → Numerical computation.
* **scikit-learn** → Statistical models and machine learning.
* **streamlit** → Interactive web interface to visualize data and EDA results.
* **pytest** → Unit and integration testing.
* **fpdf** → PDF report creation.

---
## 🧰 Tech Stack


| Category         | Tools                   |
|-----------------|--------------------------|
| Language        | Python 3.10+             |
| Data            | pandas, numpy            |
| Visualization   | matplotlib, seaborn      |
| Dashboard       | Streamlit                |
| Matching        | RapidFuzz                |
| Reporting       | FPDF                     |
| Testing         | pytest                   |
| CI/CD           | GitHub Actions           |


---

## ⚙️ Installation & Run

```bash
# 1️⃣ Clone the repo
git clone https://github.com/GeeksterLab/InteractiveNetflixEDA.git
cd InteractiveNetflixEDA

# 2️⃣ Create virtual environment
python -m venv env
source env/bin/activate

# 3️⃣ Install dependencies
make install

# 4️⃣ Run Streamlit app
make app
```

---

## 🌐 Streamlit Interface

The project includes a **Streamlit dashboard** to explore your Netflix viewing history.

Features:
- 📊 Viewing trends (year, month, day)
- 🎬 Top movies & TV shows
- 📺 TV Shows exploration (seasons & episodes)
- 🔍 Cleaned vs unmatched titles analysis

Demo: [🔗 Streamlit App](https://interactivenetflixeda.streamlit.app/)

The web interface will launch, and you can interact with your data via a visual dashboard.

---

## 🧪 Tests & Coverage

```bash
# Run all tests
make test

# Run tests with coverage report
make coverage
```

---

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
See the [LICENSE](./LICENSE) file for full details.

---
## ✨ Auteur
🏢 **AetherTech | GeeksterLab**
_Next-Level Intelligence for Next-Level Minds_
📧 [GeeksterLab@outlook.com](mailto:GeeksterLab@outlook.com)

© 2025
