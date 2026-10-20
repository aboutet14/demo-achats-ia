import streamlit as st

from lib.donnees import (extractions_corrigees, hypotheses_courantes, montant, ponderation_courante, profil,
                         scenario_actif)
from lib.negociation import economie_potentielle, preparer_plan
from lib.rapport import generer_pdf
from lib.style import DRAPEAUX, bandeau, chiffres_cles, e
from lib.tco import analyser

ROLES = {"gagnant": ("Offre recommandée", "verte"), "challenger": ("Mise en concurrence", "grise"),
         "comparaison": ("Point de comparaison", "grise"), "bloque": ("Offre bloquée", "rouge")}

scenario = scenario_actif()
besoin = scenario["besoin"]
fournisseurs = scenario["fournisseurs"]
devis = extractions_corrigees(scenario)
hyp = hypotheses_courantes(scenario)
poids, exclure_retards = ponderation_courante()
analyse = analyser(devis, besoin, fournisseurs, hyp, poids, exclure_retards)
plan = preparer_plan(devis, besoin, fournisseurs, hyp, analyse, poids)
par_id = {d["id"]: d for d in devis}


def nom_court(i):
    return f"{DRAPEAUX.get(par_id[i]['pays'], '')} {fournisseurs[i]['nom']}"


def prix(valeur, devise):
    return montant(valeur, devise) if valeur is not None else "–"


bandeau("Étape 3 sur 3 · Négociation", "Préparer la négociation, chiffres à l'appui",
        "Pour chaque fournisseur : les <b>leviers</b> tirés des écarts entre les offres, chiffrés en euros, une "
        "<b>position de négociation</b> (ouverture, objectif, limite) et un <b>brouillon d'e-mail</b> prêt à envoyer.")
st.caption("Les leviers sont calculés automatiquement à partir des devis, du coût complet et de la pondération "
           "choisie à l'étape 2. Bonne pratique : les arguments ne citent jamais le nom ni le prix d'un concurrent.")

# --- Stratégie d'ensemble ---------------------------------------------------------------------------------------
gagnant = analyse["gagnant"]
if gagnant:
    challengers = [i for i in analyse["classement"][1:] if plan[i]["position"]["role"] == "challenger"]
    eco = economie_potentielle(par_id[gagnant], analyse, plan[gagnant])
    tco_gagnant = analyse["resultats"][gagnant]["total"]
    pos = plan[gagnant]["position"]
    chiffres_cles([
        (montant(eco, decimales=0), "d'économie visée sur l'offre recommandée"),
        (f"-{eco / tco_gagnant:.1%}".replace(".", ","), "du coût complet de l'offre recommandée"),
        (prix(pos["objectif"], pos["devise"]), f"prix objectif pour {fournisseurs[gagnant]['nom']}"),
        (str(sum(len(plan[i]["leviers"]) for i in plan)), "leviers identifiés sur les 4 offres"),
    ])
    appui = (f"en s'appuyant sur <b>{e(nom_court(challengers[0]))}</b> comme alternative crédible"
             if challengers else "en s'appuyant sur l'écart avec la meilleure offre en coût complet")
    st.html(f'<div class="reco"><div class="titre">Stratégie recommandée</div>'
            f'<div class="gagnant">Négocier en priorité avec {e(nom_court(gagnant))}</div>'
            f'<p>Viser <b>{prix(pos["objectif"], pos["devise"])}</b> par unité (ouverture à '
            f'{prix(pos["ouverture"], pos["devise"])}), {appui}. Mener les deux négociations en parallèle pour '
            f'garder une vraie mise en concurrence jusqu\'à la signature.</p></div>')

pdf = generer_pdf(besoin, devis, fournisseurs, analyse, poids, plan, profil())
st.download_button("Télécharger la note de décision (PDF)", pdf, file_name="note_decision_achat.pdf",
                   mime="application/pdf", type="primary", icon=":material/download:")

# --- Détail par fournisseur -------------------------------------------------------------------------------------
st.markdown("#### Plan par fournisseur")
ordre = analyse["classement"] + [i for i in analyse["scores"] if analyse["scores"][i] is None]
for onglet, i in zip(st.tabs([nom_court(i) for i in ordre]), ordre):
    d, pf = par_id[i], plan[i]
    pos = pf["position"]
    libelle, couleur = ROLES[pos["role"]]
    with onglet:
        st.html(f'<span class="etiquette {couleur}">{e(libelle)}</span>')
        if pos["objectif"]:
            baisse = 1 - pos["objectif"] / pos["prix"]
            chiffres_cles([
                (prix(pos["prix"], pos["devise"]), "prix actuel"),
                (prix(pos["ouverture"], pos["devise"]), "prix d'ouverture (ancrage)"),
                (prix(pos["objectif"], pos["devise"]), f"objectif (-{baisse:.1%})".replace(".", ",")),
                (prix(pos["limite"], pos["devise"]), "limite à ne pas dépasser"),
            ])
        st.caption(pos["explication"])

        gauche, droite = st.columns([3, 2], gap="large")
        with gauche:
            etapes = "".join(f"<li>{e(etape)}</li>" for etape in pf["deroule"])
            st.html(f'<div class="deroule"><div class="titre">Déroulé conseillé de l\'entretien</div>'
                    f'<ol>{etapes}</ol></div>')
            st.markdown("**Leviers, du plus rentable au moins rentable** · ouvrez « Comment le négocier »")
            cartes = []
            for l in pf["leviers"]:
                c = l["conseil"]
                cartes.append(
                    f'<div class="levier"><div class="haut"><b>{e(l["titre"])}</b>'
                    f'<span class="ecart {"baisse" if l["gain"] else "neutre"}">'
                    f'{"+" + montant(l["gain"], decimales=0) if l["gain"] else e(l["nature"])}</span></div>'
                    f'<div class="arg">{e(l["argument"])}</div>'
                    f'<details><summary>Comment le négocier</summary>'
                    f'<span class="technique">{e(c["technique"])}</span>'
                    f'<p>{e(c["comment"])}</p>'
                    f'<blockquote>« {e(c["phrase"])} »</blockquote>'
                    f'<p><b>Objection probable :</b> {e(c["objection"])}<br>'
                    f'<b>Réponse :</b> {e(c["reponse"])}</p>'
                    f'<p><b>Contrepartie possible :</b> {e(c["contrepartie"])}</p></details></div>')
            st.html(f'<div class="leviers">{"".join(cartes) or "<p>Aucun levier identifié.</p>"}</div>')
        with droite:
            st.markdown("**Brouillon d'e-mail** · modifiable")
            st.caption("L'e-mail annonce le prix d'ouverture (ancrage). L'objectif et la limite restent internes.")
            st.text_area("Brouillon d'e-mail", pf["email"], height=430, key=f"email_{i}",
                         label_visibility="collapsed")

st.page_link("vues/tco.py", label="Modifier la pondération ou les hypothèses (étape 2)", icon=":material/arrow_back:")
