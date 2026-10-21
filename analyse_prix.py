import pandas as pd
import matplotlib.pyplot as plt

FICHIERS = {
    "FR": "prix_fr_2023_2025.csv",
    "DE_LU": "prix_de_2023_2025.csv",
}
FIN = pd.Timestamp("2026-01-01", tz="Europe/Paris")


def charger(fichier):
    df = pd.read_csv(fichier, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("Europe/Paris")

    # Retire l'heure en trop (1er janvier 2026 à 00:00)
    df = df[df.index < FIN]

    # Identification des heures sous zéro et colonnes temporelles utiles
    df['prix_negatif'] = df['da_price'] < 0
    df['annee'] = df.index.year
    df['mois'] = df.index.month
    df['heure'] = df.index.hour
    df['weekend'] = df.index.dayofweek >= 5  # 5 = Samedi, 6 = Dimanche
    return df


donnees = {zone: charger(fichier) for zone, fichier in FICHIERS.items()}


def tableau(cles):
    """Heures négatives groupées par `cles`, une colonne par (zone, année)."""
    return pd.concat(
        {zone: df.groupby(cles)['prix_negatif'].sum().unstack('annee')
         for zone, df in donnees.items()},
        axis=1,
    )


## --- Comparaison France / Allemagne-Luxembourg ---

print("--- Heures à prix négatif par année ---")
par_annee = pd.DataFrame(
    {zone: df.groupby('annee')['prix_negatif'].sum() for zone, df in donnees.items()}
)
print(par_annee)

print("\n--- Part des heures à prix négatif (en % des heures de l'année) ---")
part = pd.DataFrame(
    {zone: df.groupby('annee')['prix_negatif'].mean() * 100 for zone, df in donnees.items()}
)
print(part.round(2))

print("\n--- Heures à prix négatif par mois ---")
print(tableau(['mois', 'annee']))

print("\n--- Heures à prix négatif par heure du jour ---")
print(tableau(['heure', 'annee']))

print("\n--- Heures à prix négatif : Semaine (False) vs Week-end (True) ---")
print(tableau(['weekend', 'annee']))


## --- Graphiques ---

## --- Graphiques : les 3 sur une même figure ---

fig, axes = plt.subplot_mosaic(
    [["prix", "prix"],
     ["annee", "heure"]],
    figsize=(15, 10),
)

# 1. Courbes de prix FR et DE_LU (en haut, sur toute la largeur)
ax = axes["prix"]
for zone, df in donnees.items():
    df['da_price'].plot(ax=ax, linewidth=0.6, alpha=0.8, label=zone)
ax.axhline(0, color='red', linestyle='--', linewidth=1.5)  # repère y=0
ax.set_title("Évolution du prix Day-Ahead - France et Allemagne-Luxembourg - 2023 à 2025")
ax.set_ylabel("Prix (€/MWh)")
ax.set_xlabel("Date")
ax.legend()
ax.grid(True, alpha=0.3)

# 2. Heures à prix négatif par année (en bas à gauche)
ax = axes["annee"]
par_annee.plot(kind='bar', ax=ax, rot=0)
ax.set_title("Heures à prix négatif par année")
ax.set_ylabel("Nombre d'heures")
ax.set_xlabel("Année")
ax.grid(True, alpha=0.3)

# 3. Profil par heure du jour en 2025 (en bas à droite)
ax = axes["heure"]
profil_2025 = pd.DataFrame({
    zone: df[df['annee'] == 2025].groupby('heure')['prix_negatif'].sum()
    for zone, df in donnees.items()
})
profil_2025.plot(ax=ax)
ax.set_title("Heures à prix négatif par heure du jour (2025)")
ax.set_ylabel("Nombre d'heures")
ax.set_xlabel("Heure du jour")
ax.set_xticks(range(0, 24, 2))
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()