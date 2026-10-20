"""Chargement des données d'un scénario : besoin, extractions des devis, fournisseurs, hypothèses TCO."""
import copy
import json
from pathlib import Path

import streamlit as st

from lib.tco import POIDS_DEFAUT

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_SCENARIOS = RACINE / "scenarios"


def lister_scenarios():
    return sorted(d.name for d in DOSSIER_SCENARIOS.iterdir() if (d / "scenario.json").exists())


def _lire(chemin):
    return json.loads(chemin.read_text(encoding="utf-8"))


def charger_scenario(nom):
    # Pas de cache : les fichiers sont petits, et on voit ainsi toujours leur dernière version.
    dossier = DOSSIER_SCENARIOS / nom
    return {
        "dossier": dossier,
        "besoin": _lire(dossier / "scenario.json"),
        "extractions": _lire(dossier / "extractions.json")["devis"],
        "fournisseurs": {f["id"]: f for f in _lire(dossier / "fournisseurs.json")["fournisseurs"]},
        "hypotheses": _lire(dossier / "hypotheses_tco.json"),
    }


def scenario_actif():
    """Renvoie le scénario choisi dans la barre latérale."""
    return charger_scenario(st.session_state.get("scenario") or lister_scenarios()[0])


def extractions_corrigees(scenario):
    """Copie des extractions que l'acheteur peut corriger ; elle est conservée pendant toute la visite."""
    cle = f"corrections_{scenario['dossier'].name}"
    if cle not in st.session_state:
        st.session_state[cle] = copy.deepcopy(scenario["extractions"])
    return st.session_state[cle]


def hypotheses_courantes(scenario):
    """Hypothèses TCO, modifiables par le visiteur et conservées pendant toute la visite."""
    cle = f"hypotheses_{scenario['dossier'].name}"
    if cle not in st.session_state:
        st.session_state[cle] = copy.deepcopy(scenario["hypotheses"])
    return st.session_state[cle]


def ponderation_courante():
    """Poids des critères et option « éliminer les retards », conservés quand on change de page."""
    memo = st.session_state.setdefault("ponderation", {"poids": dict(POIDS_DEFAUT), "exclure": False})
    memo["poids"] = {c: st.session_state.get(f"poids_{c}", memo["poids"][c]) for c in memo["poids"]}
    memo["exclure"] = st.session_state.get("exclure_retards", memo["exclure"])
    return memo["poids"], memo["exclure"]


def profil():
    chemin = RACINE / "profil.json"
    return _lire(chemin) if chemin.exists() else {}


def reinitialiser_extractions(scenario):
    st.session_state.pop(f"corrections_{scenario['dossier'].name}", None)
    for cle in [k for k in st.session_state if k.startswith("champ_")]:
        del st.session_state[cle]


def montant(valeur, devise="EUR", decimales=2):
    """Format français : 28 430,00 €."""
    texte = f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return f"{texte} €" if devise == "EUR" else f"{texte} {devise}"
