"""Point d'entrée de l'application. Lancement : .venv/bin/streamlit run app.py"""
import streamlit as st

from lib.donnees import lister_scenarios, profil
from lib.style import appliquer_style, e

st.set_page_config(page_title="Achats × IA – démonstration", page_icon="📊", layout="wide")
appliquer_style()
st.logo("assets/logo.svg", size="large", icon_image="assets/logo_icone.svg")

scenarios = lister_scenarios()
if len(scenarios) > 1:
    st.sidebar.selectbox("Scénario", scenarios, key="scenario")

page = st.navigation([
    st.Page("vues/accueil.py", title="Accueil", icon=":material/home:", default=True),
    st.Page("vues/extraction.py", title="1. Extraction des devis", icon=":material/document_scanner:"),
    st.Page("vues/tco.py", title="2. TCO et décision", icon=":material/balance:"),
    st.Page("vues/negociation.py", title="3. Négociation", icon=":material/handshake:"),
    st.Page("vues/kpi.py", title="4. Suivi fournisseur (KPI)", icon=":material/monitoring:"),
    st.Page("vues/methodologie.py", title="Méthodologie", icon=":material/info:"),
])

auteur = profil()
if auteur.get("nom"):
    lien = f'<br><a href="{e(auteur["linkedin"])}" target="_blank">Profil LinkedIn →</a>' if auteur.get("linkedin") else ""
    st.sidebar.html(f'<div class="profil">Projet réalisé par<br><b>{e(auteur["nom"])}</b><br>'
                    f'{e(auteur.get("titre", ""))}{lien}</div>')
st.sidebar.caption("Démonstration : toutes les entreprises et données sont fictives.")
page.run()
