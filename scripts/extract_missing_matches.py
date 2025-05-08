import pandas as pd
from datetime import datetime


# Charger le fichier enrichi
df = pd.read_csv('data/processed/enriched_netflix_history2.csv')

# Filtrer uniquement les titres non trouvés (Matched_Title vide)
missing_data = df[df['Matched_Title'].isna()]

# Générer un timestamp pour créer des noms de fichiers uniques
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


# Sauvegarder dans un fichier CSV pour analyse
output_file = f'../data/processed/missing_matched_titles_{timestamp}.csv'
missing_data.to_csv(output_file, index=False)

# Afficher un extrait des titres non trouvés
print(f"⚠️ {len(missing_data)} titres n'ont pas été appariés !")
print(missing_data[['Date Watched', 'Title']].head(10))

print(f"✅ Fichier de debug sauvegardé : {output_file}")
