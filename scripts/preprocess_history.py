import pandas as pd
import csv

def preprocess_csv(input_file, output_file):
    # Lire le fichier CSV
    df = pd.read_csv(input_file, encoding='utf-8')
    
    # Supprimer tous les guillemets dans la colonne Title
    df['Title'] = df['Title'].str.replace(r'[\"“”]', '', regex=True)
    
    # Pour les titres contenant "Partie", remplacer "Partie" par "Saison"
    df['Title'] = df['Title'].str.replace('Partie', 'Saison', regex=False)
    
    # Sauvegarder le fichier prétraité en n'ajoutant aucun guillemet
    # df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Les guillemets ont été supprimés et le fichier est sauvegardé sous {output_file}")

if __name__ == '__main__':
    input_file = '../data/raw/ViewingActivity.csv'
    output_file = '../data/raw/ViewingActivity2.csv'
    preprocess_csv(input_file, output_file)
