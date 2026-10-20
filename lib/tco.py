"""Calcul du coût complet (TCO) de chaque offre et de la matrice de décision pondérée."""
import math
from datetime import date, timedelta

# Chaque poste de coût appartient à une famille (utilisée pour le graphique).
FAMILLES = ["Prix d'achat", "Frais fixes et qualification", "Logistique et douane",
            "Financier et change", "Qualité et excédent"]
POSTES = {
    "Achat (quantité utile)": "Prix d'achat",
    "Frais fixes (outillage, emballage)": "Frais fixes et qualification",
    "Qualification du fournisseur": "Frais fixes et qualification",
    "Transport et assurance": "Logistique et douane",
    "Douane et formalités": "Logistique et douane",
    "Escompte obtenu": "Financier et change",
    "Coût (+) ou gain (−) de trésorerie": "Financier et change",
    "Provision risque de change": "Financier et change",
    "Non-qualité estimée": "Qualité et excédent",
    "Excédent non utilisé": "Qualité et excédent",
}

CRITERES = {
    "cout": "Coût complet (TCO)",
    "delai": "Délai",
    "qualite": "Qualité",
    "risque": "Risque fournisseur",
    "paiement": "Conditions de paiement",
}
COURTS = {"cout": "Coût", "delai": "Délai", "qualite": "Qualité", "risque": "Risque", "paiement": "Paiement"}
POIDS_DEFAUT = {"cout": 40, "delai": 15, "qualite": 20, "risque": 15, "paiement": 10}

PAYS_UE = {"Allemagne", "Autriche", "Belgique", "Bulgarie", "Chypre", "Croatie", "Danemark", "Espagne", "Estonie",
           "Finlande", "France", "Grèce", "Hongrie", "Irlande", "Italie", "Lettonie", "Lituanie", "Luxembourg",
           "Malte", "Pays-Bas", "Pologne", "Portugal", "Roumanie", "Slovaquie", "Slovénie", "Suède", "Tchéquie"}


def taux_vers_eur(devise, hyp):
    return 1.0 if devise == "EUR" else 1 / hyp["generales"]["taux_change"][devise]


def calculer_tco(d, besoin, hyp):
    """Coût complet en euros pour couvrir le besoin, poste par poste."""
    hg = hyp["generales"]
    hf = hyp["par_fournisseur"][d["id"]]
    taux = taux_vers_eur(d["devise"], hyp)
    qte_besoin = besoin["quantite"]
    qte_commandee = max(qte_besoin, d["quantite_minimum"])
    excedent = qte_commandee - qte_besoin
    prix_eur = d["prix_unitaire"] * taux
    frais_fixes = sum(f["montant"] or 0 for f in d["frais_fixes"]) * taux
    montant_devis = prix_eur * qte_commandee + frais_fixes

    date_commande = date.fromisoformat(hg["date_commande"])
    livraison = date_commande + timedelta(
        days=round(hg["bat_jours"] + d["delai_semaines"] * 7 + hf["transit_jours"]))
    jours_commande_livraison = (livraison - date_commande).days

    def jours_moyens(jours_solde):
        """Date moyenne de paiement, en jours après la livraison (négatif = payé avant)."""
        acompte = d["acompte_pct"] / 100
        return -acompte * jours_commande_livraison + (1 - acompte) * jours_solde

    def tresorerie(jours_solde, montant):
        # Référence : paiement le jour de la livraison. Payer plus tard rapporte, payer avant coûte.
        return -montant * hg["taux_financement_annuel"] * jours_moyens(jours_solde) / 365

    escompte = 0.0
    cout_tresorerie = tresorerie(d["jours_paiement"], montant_devis)
    if d["escompte_pct"]:
        remise = montant_devis * d["escompte_pct"] / 100
        avec_escompte = tresorerie(d["escompte_jours"], montant_devis - remise)
        if avec_escompte - remise < cout_tresorerie:
            escompte, cout_tresorerie = -remise, avec_escompte

    transport = hf["transport_eur"]
    postes = {
        "Achat (quantité utile)": prix_eur * qte_besoin,
        "Frais fixes (outillage, emballage)": frais_fixes,
        "Qualification du fournisseur": hf["cout_qualification_eur"],
        "Transport et assurance": transport + hf["taux_assurance_transport"] * montant_devis,
        "Douane et formalités": hf["taux_droits_douane"] * (montant_devis + transport)
                                + hf["dedouanement_export_eur"] + hf["dedouanement_import_eur"],
        "Escompte obtenu": escompte,
        "Coût (+) ou gain (−) de trésorerie": cout_tresorerie,
        "Provision risque de change": hg["provision_risque_change"] * montant_devis if d["devise"] != "EUR" else 0,
        "Non-qualité estimée": hf["taux_defaut_estime"] * qte_besoin * hg["cout_par_defaut_qualite_eur"],
        "Excédent non utilisé": excedent * prix_eur * (1 - hg["valeur_residuelle_excedent"])
                                + math.ceil(excedent / hg["presentoirs_par_palette"])
                                * hg["cout_stockage_palette_mois_eur"] * hg["duree_stockage_excedent_mois"],
    }
    total = sum(postes.values())
    return {
        "postes": postes,
        "total": total,
        "unitaire": total / qte_besoin,
        "prix_affiche_eur": prix_eur,
        "montant_devis": montant_devis,
        "qte_commandee": qte_commandee,
        "excedent": excedent,
        "livraison": livraison,
        "marge_jours": (date.fromisoformat(besoin["date_besoin"]) - livraison).days,
        "escompte_pris": escompte < 0,
        "jours_paiement_moyens": jours_moyens(d["jours_paiement"]),
    }


def borner(note):
    return max(0.0, min(10.0, note))


def noter(devis, resultats, fournisseurs, hyp):
    """Note de 0 à 10 par critère. Les règles sont expliquées dans la page."""
    tco_min = min(r["total"] for r in resultats.values())
    notes = {}
    for d in devis:
        r, f = resultats[d["id"]], fournisseurs[d["id"]]
        hf = hyp["par_fournisseur"][d["id"]]
        autres_risques = 10 - 4 * f["incidents_paiement"] - 3 * (f["pays"] not in PAYS_UE)
        notes[d["id"]] = {
            "cout": 10 * tco_min / r["total"],
            "delai": 0.0 if r["marge_jours"] < 0 else borner(5 + r["marge_jours"] / 21 * 5),
            "qualite": borner(10 - hf["taux_defaut_estime"] * 200 - ("ISO 9001" not in f["certifications"])),
            "risque": borner(0.7 * f["note_solvabilite_sur_20"] / 2 + 0.3 * autres_risques),
            "paiement": borner((r["jours_paiement_moyens"] + 30) / 90 * 10),
        }
    return notes


def score_pondere(notes, poids):
    total_poids = sum(poids.values()) or 1
    return sum(notes[c] * poids[c] for c in CRITERES) / total_poids


def analyser(devis, besoin, fournisseurs, hyp, poids, exclure_retards):
    """TCO, notes, scores et classement : la même analyse sert aux pages TCO, Négociation et au PDF."""
    resultats = {d["id"]: calculer_tco(d, besoin, hyp) for d in devis}
    notes = noter(devis, resultats, fournisseurs, hyp)
    scores = {d["id"]: None if exclure_retards and resultats[d["id"]]["marge_jours"] < 0
              else score_pondere(notes[d["id"]], poids) for d in devis}
    classement = sorted((i for i in scores if scores[i] is not None), key=scores.get, reverse=True)
    return {
        "resultats": resultats,
        "notes": notes,
        "scores": scores,
        "classement": classement,
        "gagnant": classement[0] if classement else None,
        "moins_cher_devis": min(devis, key=lambda d: resultats[d["id"]]["prix_affiche_eur"])["id"],
        "moins_cher_tco": min(devis, key=lambda d: resultats[d["id"]]["total"])["id"],
    }
