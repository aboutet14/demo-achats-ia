# Achats × IA : comparer des devis fournisseurs avec l'IA

Application de démonstration créée par **Alexis Boutet**, acheteur ([LinkedIn](https://www.linkedin.com/in/boutetalexis/)).

👉 **Voir l'application en ligne :** *lien à venir*

## Ce que montre la démonstration

Un acheteur consulte 4 fournisseurs européens et turc pour 2 000 présentoirs PLV en carton.

1. **Extraction** : l'IA lit des devis aux formats, langues et devises différents (PDF, e-mail, pro forma en dollars), en tire les données clés et signale les pièges.
2. **Coût complet (TCO) et décision** : transport, douane, outillage, trésorerie, change, non-qualité et excédent sont ajoutés au prix. Une matrice pondérée, réglable par le visiteur, classe les offres.
3. **Négociation** : leviers chiffrés par fournisseur, prix d'ouverture, objectif et limite, conseils de négociation, brouillon d'e-mail et note de décision en PDF.

Toutes les entreprises et toutes les données sont **fictives**.

## Lancer l'application sur son ordinateur

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## Organisation du projet

| Dossier | Contenu |
|---|---|
| `app.py` | Point d'entrée et menu |
| `vues/` | Les pages de l'application |
| `lib/` | Calculs (TCO, notes, négociation), conseils, export PDF, style |
| `scenarios/` | Un dossier par cas d'achat : devis, extractions, fournisseurs, hypothèses |
| `outils/` | Génération des devis factices |

Pour présenter un autre cas d'achat, il suffit d'ajouter un dossier dans `scenarios/`.
