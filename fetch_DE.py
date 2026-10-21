
from entsoe_data import fetch_range
import pandas as pd

# Période d'étude : premier semestre 2023
start = "2023-01-01"
end = "2025-12-31"

# Récupération des prix
prix = fetch_range("DE_LU", start, end)

# Sauvegarde des données
prix.to_csv("prix_de_2023_2025.csv")

# Vérification
print("\n--- Résultat de la collecte ---")
print("Nombre de valeurs :", len(prix))
print("Première date :", prix.index.min())
print("Dernière date :", prix.index.max())
print("Valeurs manquantes :", prix.isna().sum())
print("Doublons :", prix.index.duplicated().sum())
print("\nFichier sauvegardé.")
