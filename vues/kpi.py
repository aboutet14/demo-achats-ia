"""Après l'attribution : pilotage du fournisseur recommandé (gain de négociation, suivi mensuel, scorecard)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib.donnees import extractions_corrigees, hypotheses_courantes, montant, ponderation_courante, scenario_actif
from lib.negociation import preparer_plan
from lib.style import DRAPEAUX, bandeau, chiffres_cles, e, liste_alertes
from lib.tco import analyser

# Même palette que la page TCO.
COULEURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
# Mois numérotés : l'ordre reste correct même si un graphique trie les libellés.
MOIS = ["01 Jan", "02 Fév", "03 Mar", "04 Avr", "05 Mai", "06 Juin"]
# Colonnes saisies dans le tableau de suivi, avec l'aide affichée au survol de leur titre.
AIDE = {
    "Commandes": "Nombre de commandes passées dans le mois",
    "Quantité commandée": "Unités commandées dans le mois",
    "Quantité reçue": "Unités réellement livrées",
    "Quantité non conforme": "Unités reçues refusées au contrôle (défaut d'impression, carton abîmé…)",
    "Livrées à l'heure": "Commandes livrées à la date confirmée",
    "Livrées complètes": "Commandes livrées sans manquant",
    "Prix facturé (€/u)": "Prix unitaire figurant sur la facture",
}
COLONNES = list(AIDE)

scenario = scenario_actif()
besoin = scenario["besoin"]
fournisseurs = scenario["fournisseurs"]
devis = extractions_corrigees(scenario)
hyp = hypotheses_courantes(scenario)
poids, exclure_retards = ponderation_courante()
analyse = analyser(devis, besoin, fournisseurs, hyp, poids, exclure_retards)
plan = preparer_plan(devis, besoin, fournisseurs, hyp, analyse, poids)
par_id = {d["id"]: d for d in devis}


def fr(valeur, decimales=1, signe=False):
    """Nombre au format français : 6 693 ou 93,5 (ou +93,5 avec signe=True)."""
    return f"{valeur:{'+' if signe else ''},.{decimales}f}".replace(",", " ").replace(".", ",")


gagnant = analyse["gagnant"]
if not gagnant:
    bandeau("Après l'attribution · Suivi fournisseur", "Piloter le fournisseur retenu",
            "Aucune offre n'est retenue avec les réglages actuels de l'étape 2.")
    st.page_link("vues/tco.py", label="Revenir à l'étape 2", icon=":material/arrow_back:")
    st.stop()

d = par_id[gagnant]
r = analyse["resultats"][gagnant]
pos = plan[gagnant]["position"]
nom = f"{DRAPEAUX.get(d['pays'], '')} {fournisseurs[gagnant]['nom']}"
taux = r["prix_affiche_eur"] / d["prix_unitaire"]  # devise du devis -> €
prix_devis = r["prix_affiche_eur"]
qte = r["qte_commandee"]

bandeau("Après l'attribution · Suivi fournisseur", "Piloter le fournisseur retenu",
        f"<b>{e(nom)}</b> est l'offre recommandée à l'étape 2. On mesure d'abord le gain obtenu en négociation, "
        "puis on suit chaque mois quantités, délai, qualité et prix facturé : la <b>scorecard</b> dit s'il faut agir.")

# --- 1. Résultat de la négociation -----------------------------------------------------------------------------
st.subheader("1. Résultat de la négociation")
prix_signe = st.number_input(
    "Prix unitaire signé (€)", min_value=0.01, value=round(pos["objectif"] * taux if pos["objectif"] else prix_devis, 2),
    step=0.05, format="%.2f",
    help="Proposé par défaut : le prix objectif calculé à l'étape 3. Remplacez-le par le prix réellement obtenu.")

moyenne_offres = sum(analyse["resultats"][x["id"]]["prix_affiche_eur"] for x in devis) / len(devis)
gain = (prix_devis - prix_signe) * qte
saving = (moyenne_offres - prix_signe) * qte
chiffres_cles([
    (montant(gain, decimales=0), f"gagnés en négociation ({fr(-(prix_devis - prix_signe) / prix_devis * 100)} % "
                                 f"vs devis à {montant(prix_devis)})"),
    (montant(saving, decimales=0), f"d'économie vs la moyenne des {len(devis)} offres reçues"),
    (montant(prix_signe * qte, decimales=0), f"de dépense engagée ({fr(qte, 0)} {besoin['unite']})"),
    (f"{d['jours_paiement']} jours", "de délai de paiement moyen après facture"),
])

# --- 2. Suivi opérationnel mensuel -----------------------------------------------------------------------------
st.subheader("2. Suivi opérationnel mensuel")
st.caption("Données fictives : 6 mois de réassorts après le lancement. Le tableau est modifiable (changez un "
           "chiffre, ajoutez un mois) : tous les indicateurs se recalculent.")

cle = f"suivi_{scenario['dossier'].name}_{gagnant}_{prix_signe:.2f}"
if cle not in st.session_state:
    st.session_state[cle] = pd.DataFrame({
        "Mois": MOIS,
        "Commandes": [3, 4, 2, 5, 4, 3],
        "Quantité commandée": [600, 800, 400, 1000, 800, 600],
        "Quantité reçue": [600, 790, 400, 1000, 760, 600],
        "Quantité non conforme": [1, 4, 0, 6, 0, 0],
        "Livrées à l'heure": [3, 3, 2, 4, 4, 3],
        "Livrées complètes": [3, 3, 2, 5, 3, 3],
        "Prix facturé (€/u)": [prix_signe] * 3 + [round(prix_signe + 0.15, 2)] + [prix_signe] * 2,
    })

suivi = st.data_editor(
    st.session_state[cle], num_rows="dynamic", width="stretch", hide_index=True, key=f"editeur_{cle}",
    column_config={c: st.column_config.NumberColumn(c, min_value=0, format="%.2f" if "Prix" in c else "%d",
                                                    help=AIDE[c])
                   for c in COLONNES})

# Les lignes incomplètes, sans commande ou sans quantité reçue, sont ignorées dans les calculs.
df = suivi.dropna(subset=["Mois", *COLONNES]).copy()
df = df[(df["Commandes"] > 0) & (df["Quantité commandée"] > 0) & (df["Quantité reçue"] > 0)]
if df.empty:
    st.info("Complétez au moins un mois (commandes, quantité commandée et quantité reçue supérieures à 0) pour "
            "calculer les indicateurs.")
    st.stop()
df["Mois"] = df["Mois"].astype(str)
df["OTD %"] = (df["Livrées à l'heure"] / df["Commandes"] * 100).clip(upper=100)
df["Taux de service %"] = (df["Livrées complètes"] / df["Commandes"] * 100).clip(upper=100)
df["Non-conformité %"] = df["Quantité non conforme"] / df["Quantité reçue"] * 100
df["Écart prix %"] = (df["Prix facturé (€/u)"] - prix_signe) / prix_signe * 100

qte_commandee = df["Quantité commandée"].sum()
qte_recue = df["Quantité reçue"].sum()
facture = (df["Quantité reçue"] * df["Prix facturé (€/u)"]).sum()
st.caption(f"Sur la période : {fr(qte_commandee, 0)} {besoin['unite']} commandés, {fr(qte_recue, 0)} reçus "
           f"({fr(qte_recue / qte_commandee * 100)} %), {montant(facture, decimales=0)} facturés.")

with st.expander("Objectifs contractuels", icon=":material/flag:"):
    o1, o2, o3 = st.columns(3)
    obj_otd = o1.number_input("OTD cible (%)", min_value=1.0, max_value=100.0, value=95.0)
    obj_service = o2.number_input("Taux de service cible (%)", min_value=1.0, max_value=100.0, value=98.0)
    obj_nc = o3.number_input("Non-conformité maximum (%)", min_value=0.01, max_value=100.0, value=0.5, step=0.1)

otd = df["OTD %"].mean()
service = df["Taux de service %"].mean()
non_conformite = df["Quantité non conforme"].sum() / qte_recue * 100
surfacturation = max(0.0, df["Écart prix %"].max())  # une facture sous le prix signé n'est pas une faute

k1, k2, k3, k4 = st.columns(4)
k1.metric("OTD moyen (livré à l'heure)", f"{fr(otd)} %", f"{fr(otd - obj_otd, signe=True)} pts vs cible", border=True)
k2.metric("Taux de service (livré complet)", f"{fr(service)} %", f"{fr(service - obj_service, signe=True)} pts vs cible",
          border=True)
k3.metric("Qualité (produits non conformes)", f"{fr(non_conformite, 2)} %",
          f"{fr(non_conformite - obj_nc, 2, signe=True)} pts vs maximum", delta_color="inverse", border=True)
k4.metric("Surfacturation maximale", f"{fr(surfacturation)} %",
          "Conforme" if surfacturation == 0 else "À vérifier",
          delta_color="off" if surfacturation == 0 else "inverse", border=True)


def graphique(titre, series, cible, nom_cible):
    fig = go.Figure()
    for (libelle, colonne, type_), couleur in zip(series, COULEURS):
        if type_ == "barre":
            fig.add_bar(name=libelle, x=df["Mois"], y=df[colonne], marker_color=couleur)
        else:
            fig.add_scatter(name=libelle, x=df["Mois"], y=df[colonne], mode="lines+markers",
                            line=dict(color=couleur, width=3))
    fig.add_hline(y=cible, line=dict(color="#C2413B", dash="dash", width=2),
                  annotation_text=nom_cible, annotation_position="top left")
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), title=dict(text=titre, font=dict(size=15)),
                      legend=dict(orientation="h", y=-0.2), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="Inter, sans-serif", color="#16243A"),
                      xaxis=dict(type="category"), yaxis=dict(gridcolor="#E6E9EE", ticksuffix=" %"))
    st.plotly_chart(fig, width="stretch")


g1, g2 = st.columns(2)
with g1, st.container(border=True):
    graphique("Ponctualité et service (%)",
              [("OTD", "OTD %", "ligne"), ("Taux de service", "Taux de service %", "ligne")], obj_otd, "OTD cible")
with g2, st.container(border=True):
    graphique("Produits non conformes (% des quantités reçues)",
              [("Non-conformité", "Non-conformité %", "barre")], obj_nc, "Maximum contractuel")

# --- 3. Scorecard fournisseur ----------------------------------------------------------------------------------
st.subheader("3. Scorecard fournisseur")
w1, w2, w3, w4 = st.columns(4)
p_otd = w1.slider("Poids délai", 0, 100, 35)
p_qual = w2.slider("Poids qualité", 0, 100, 30)
p_prix = w3.slider("Poids prix", 0, 100, 20)
p_serv = w4.slider("Poids service", 0, 100, 15)
total_poids = max(p_otd + p_qual + p_prix + p_serv, 1)

notes = {
    "Délai (OTD)": min(otd / obj_otd, 1) * 100,
    "Qualité": max(0, 100 - non_conformite / obj_nc * 50),  # 0 % = 100, maximum contractuel = 50
    "Prix facturé": max(0, 100 - surfacturation * 20),  # chaque % de surfacturation = -20 pts
    "Service": min(service / obj_service, 1) * 100,
}
poids_kpi = [p_otd, p_qual, p_prix, p_serv]
score = sum(n * p for n, p in zip(notes.values(), poids_kpi)) / total_poids

if score >= 85:
    statut, action, couleur = "Fournisseur performant", "Maintenir le suivi mensuel.", "#1F8A5B"
elif score >= 70:
    statut, action, couleur = ("Sous surveillance", "Revue de performance avec le fournisseur et plan d'action "
                               "correctif daté.", "#C77A12")
else:
    statut, action, couleur = ("Non conforme", "Escalade, pénalités contractuelles et re-sourcing à envisager.",
                               "#C2413B")

s1, s2 = st.columns([1, 2])
s1.metric("Score global", f"{score:.0f} / 100", border=True)
s2.html(f'<div class="reco" style="border-left-color:{couleur}; margin-top:0">'
        f'<div class="titre" style="color:{couleur}">Statut</div><div class="gagnant">{e(statut)}</div>'
        f'<p>{e(action)}</p></div>')

st.dataframe(pd.DataFrame({
    "Critère": list(notes),
    "Note /100": [round(n) for n in notes.values()],
    "Poids %": [round(p / total_poids * 100) for p in poids_kpi],
}), hide_index=True, width="stretch")

# --- 4. Alertes ------------------------------------------------------------------------------------------------
st.subheader("4. Alertes")
alertes = []
for _, ligne in df.iterrows():
    if ligne["OTD %"] < obj_otd:
        alertes.append(f"{ligne['Mois']} : OTD à {fr(ligne['OTD %'], 0)} % (cible {fr(obj_otd, 0)} %)")
    if ligne["Quantité reçue"] < ligne["Quantité commandée"]:
        manque = ligne["Quantité commandée"] - ligne["Quantité reçue"]
        alertes.append(f"{ligne['Mois']} : {fr(manque, 0)} {besoin['unite']} manquants sur "
                       f"{fr(ligne['Quantité commandée'], 0)} commandés")
    if ligne["Non-conformité %"] > obj_nc:
        alertes.append(f"{ligne['Mois']} : {fr(ligne['Non-conformité %'], 2)} % de produits non conformes "
                       f"(maximum {fr(obj_nc, 2)} %)")
    if ligne["Écart prix %"] > 0:
        alertes.append(f"{ligne['Mois']} : prix facturé supérieur au prix signé (+{fr(ligne['Écart prix %'])} %)")
liste_alertes(alertes)
