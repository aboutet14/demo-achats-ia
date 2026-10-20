import pandas as pd
import streamlit as st

from lib.donnees import extractions_corrigees, montant, reinitialiser_extractions, scenario_actif
from lib.style import DRAPEAUX, bandeau, liste_alertes

INCOTERMS = ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DPU", "DDP"]
DEVISES = ["EUR", "USD", "GBP", "CHF", "PLN"]

scenario = scenario_actif()
originaux = {d["id"]: d for d in scenario["extractions"]}
devis = extractions_corrigees(scenario)

bandeau("Étape 1 sur 3 · Extraction", "L'IA lit les devis à votre place",
        "Quatre fournisseurs, quatre documents différents : un devis français, un devis en anglais, un simple "
        "e-mail et une pro forma en dollars. <b>L'IA en extrait les mêmes informations dans un format commun</b> "
        "et signale les pièges ; l'acheteur vérifie et corrige.")
st.caption("Mode démonstration : les extractions ont été réalisées par IA (Claude) puis enregistrées, "
           "pour que la page fonctionne sans coût ni attente.")


def total_frais_fixes(d):
    return sum(f["montant"] for f in d["frais_fixes"])


def montant_devis(d):
    return d["prix_unitaire"] * max(d["quantite_proposee"], d["quantite_minimum"]) + total_frais_fixes(d)


def texte_paiement(d):
    morceaux = []
    if d["acompte_pct"]:
        morceaux.append(f"{d['acompte_pct']:g} % à la commande")
    jours = d["jours_paiement"]
    morceaux.append(f"solde {jours} j après livraison" if jours >= 0 else f"solde {-jours} j avant livraison")
    if d["escompte_pct"]:
        morceaux.append(f"escompte {d['escompte_pct']:g} % à {d['escompte_jours']} j")
    return ", ".join(morceaux)


# --- Vue d'ensemble -------------------------------------------------------------------------------------------
st.subheader("Vue d'ensemble : les 4 offres dans un format commun")
st.dataframe(
    pd.DataFrame([{
        "Fournisseur": f"{DRAPEAUX.get(d['pays'], '')} {d['fournisseur']}",
        "Document": f"{d['format']} ({d['langue'].lower()})",
        "Prix unitaire": montant(d["prix_unitaire"], d["devise"]),
        "Quantité": d["quantite_proposee"],
        "Frais fixes": montant(total_frais_fixes(d), d["devise"], 0),
        "Montant du devis (HT)": montant(montant_devis(d), d["devise"], 0),
        "Incoterm": f"{d['incoterm']} {d['lieu_incoterm']}",
        "Délai": f"{d['delai_semaines']:g} sem.",
        "Paiement": texte_paiement(d),
        "Validité": f"{d['validite_jours']} j",
        "Alertes": len(d["points_attention"]),
    } for d in devis]),
    hide_index=True, width="stretch",
)
st.caption("Attention : à ce stade, les prix ne sont **pas comparables** (devises, incoterms, frais fixes et "
           "quantités différents). C'est l'objet de l'étape 2 : le TCO.")

# --- Détail par devis -----------------------------------------------------------------------------------------
st.subheader("Détail : document original et données extraites")
onglets = st.tabs([f"{DRAPEAUX.get(d['pays'], '')} {d['fournisseur'].split(' Sp.')[0].split(',')[0]}" for d in devis])

for onglet, d in zip(onglets, devis):
    origine = originaux[d["id"]]
    with onglet:
        gauche, droite = st.columns([1, 1], gap="large")

        with gauche:
            st.markdown(f"**Document reçu** · {d['format']} en {d['langue'].lower()}")
            fichier = scenario["dossier"] / "devis" / d["fichier"]
            if fichier.suffix == ".pdf":
                st.image(str(fichier.parent / "apercus" / f"{fichier.stem}.png"), width="stretch")
                st.download_button("Télécharger le PDF", fichier.read_bytes(), file_name=fichier.name,
                                   mime="application/pdf", key=f"dl_{d['id']}")
            else:
                with st.container(border=True, height=620):
                    st.text(fichier.read_text(encoding="utf-8"))

        with droite:
            st.markdown("**Données extraites par l'IA** · modifiables")
            cle = f"champ_{d['id']}_"
            c1, c2 = st.columns(2)
            d["prix_unitaire"] = c1.number_input("Prix unitaire", value=float(d["prix_unitaire"]), step=0.05,
                                                 format="%.2f", key=cle + "prix")
            d["devise"] = c2.selectbox("Devise", DEVISES, index=DEVISES.index(d["devise"]), key=cle + "devise")
            d["quantite_proposee"] = c1.number_input("Quantité proposée", value=int(d["quantite_proposee"]),
                                                     step=100, key=cle + "qte")
            d["quantite_minimum"] = c2.number_input("Minimum de commande (0 = aucun)",
                                                    value=int(d["quantite_minimum"]), step=100, key=cle + "moq")
            d["incoterm"] = c1.selectbox("Incoterm", INCOTERMS, index=INCOTERMS.index(d["incoterm"]),
                                         key=cle + "incoterm")
            d["lieu_incoterm"] = c2.text_input("Lieu", value=d["lieu_incoterm"], key=cle + "lieu")
            d["delai_semaines"] = c1.number_input("Délai (semaines)", value=float(d["delai_semaines"]), step=0.5,
                                                  format="%.1f", key=cle + "delai", help=d["delai_point_depart"])
            d["validite_jours"] = c2.number_input("Validité de l'offre (jours)", value=int(d["validite_jours"]),
                                                  step=5, key=cle + "validite")

            st.markdown("**Conditions de paiement**")
            st.caption(f"Texte du devis : « {d['paiement_texte']} »")
            p1, p2, p3, p4 = st.columns(4)
            d["acompte_pct"] = p1.number_input("Acompte (%)", value=float(d["acompte_pct"]), step=5.0,
                                               format="%g", key=cle + "acompte")
            d["jours_paiement"] = p2.number_input("Solde (j / livraison)", value=int(d["jours_paiement"]), step=5,
                                                  key=cle + "jours", help=d["jours_paiement_note"] or
                                                  "Jours entre la livraison et le paiement (négatif = avant)")
            d["escompte_pct"] = p3.number_input("Escompte (%)", value=float(d["escompte_pct"]), step=0.5,
                                                format="%g", key=cle + "escompte")
            d["escompte_jours"] = p4.number_input("Escompte à (j)", value=int(d["escompte_jours"]), step=5,
                                                  key=cle + "escompte_j")

            st.markdown("**Frais fixes** (outillage, emballage…)")
            frais = st.data_editor(pd.DataFrame(d["frais_fixes"]), num_rows="dynamic", hide_index=True,
                                   width="stretch", key=cle + "frais",
                                   column_config={"libelle": "Libellé", "note": "Remarque",
                                                  "montant": st.column_config.NumberColumn(
                                                      f"Montant ({d['devise']})", format="%.0f")})
            d["frais_fixes"] = frais.fillna({"montant": 0, "libelle": "", "note": ""}).to_dict("records")

            st.metric("Montant total du devis (HT)", montant(montant_devis(d), d["devise"]), border=True,
                      help="Prix unitaire × quantité commandée + frais fixes. Hors transport, douane et "
                           "autres coûts : voir l'étape 2 (TCO).")

            with st.expander("Autres conditions extraites"):
                st.markdown(f"- **Remise sur volume** : {d['remise_volume']}\n"
                            f"- **Tolérance de quantité** : {d['tolerance_quantite']}\n"
                            f"- **Révision de prix** : {d['revision_prix']}\n" +
                            "".join(f"- {c}\n" for c in d["conditions_particulieres"]))

            st.markdown("**Points d'attention repérés par l'IA**")
            liste_alertes(d["points_attention"])

            modifies = [k for k in ("prix_unitaire", "devise", "quantite_proposee", "quantite_minimum", "incoterm",
                                    "lieu_incoterm", "delai_semaines", "validite_jours", "acompte_pct",
                                    "jours_paiement", "escompte_pct", "escompte_jours", "frais_fixes")
                        if d[k] != origine[k]]
            if modifies:
                st.info(f"{len(modifies)} valeur(s) corrigée(s) par l'acheteur : elles seront utilisées dans la "
                        "suite de l'analyse.", icon=":material/edit:")

if st.button("Annuler toutes les corrections", icon=":material/restart_alt:"):
    reinitialiser_extractions(scenario)
    st.rerun()
