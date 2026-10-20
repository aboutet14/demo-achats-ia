import streamlit as st

from lib.donnees import extractions_corrigees, hypotheses_courantes, scenario_actif
from lib.style import bandeau, chiffres_cles, e
from lib.tco import calculer_tco

scenario = scenario_actif()
besoin = scenario["besoin"]
devis = extractions_corrigees(scenario)
resultats = [calculer_tco(d, besoin, hypotheses_courantes(scenario)) for d in devis]

bandeau("Démonstration · Achats & IA", "Comparer des devis fournisseurs avec l'IA",
        "Lire des devis hétérogènes, calculer le <b>coût complet</b> de chaque offre, décider selon des "
        "<b>critères pondérés</b> et préparer la <b>négociation</b>. Le tout en quelques minutes.")

ecart_max = max((r["unitaire"] - r["prix_affiche_eur"]) / r["prix_affiche_eur"] for r in resultats)
chiffres_cles([
    (f"{len(devis)} devis", f"{len({d['format'] for d in devis})} formats, "
                            f"{len({d['langue'] for d in devis})} langues, {len({d['devise'] for d in devis})} devises"),
    (f"{besoin['quantite']:,}".replace(",", " "), besoin["unite"] + " à acheter"),
    (f"+{ecart_max:.0%}".replace(".", ","), "d'écart maximal entre prix affiché et coût réel"),
    (str(sum(len(d["points_attention"]) for d in devis)), "points d'attention repérés par l'IA"),
])

col_cas, col_lecture = st.columns([3, 2], gap="medium")
with col_cas.container(border=True):
    st.markdown("#### Le cas étudié")
    st.markdown(f"**{e(besoin['titre'])}** pour {e(besoin['acheteur'])}.  \n{e(besoin['produit'])}.")
    st.markdown(f"Livraison au plus tard le **{'/'.join(reversed(besoin['date_besoin'].split('-')))}** à "
                f"{e(besoin['lieu_livraison'])}.  \n*{e(besoin['commentaire_besoin'])}*")
with col_lecture.container(border=True):
    st.markdown("#### À voir en 2 minutes")
    st.markdown("1. **Extraction** : un e-mail, une pro forma en dollars, deux devis PDF… l'IA les met au même format.\n"
                "2. **TCO** : le moins cher sur le devis n'est pas le moins cher au final.\n"
                "3. **Décision** : bougez les curseurs, le classement change.\n"
                "4. **Négociation** : leviers chiffrés, e-mail prêt à envoyer et note de décision en PDF.")

st.markdown("#### Le parcours")
etapes = [
    ("1", "Extraction des devis", "L'IA lit des documents de formats, langues et devises différents, en tire les "
     "données clés et signale les pièges. L'acheteur vérifie et corrige.", "vues/extraction.py"),
    ("2", "TCO et matrice de décision", "Coût complet par fournisseur (transport, douane, trésorerie, change, "
     "qualité…) puis score pondéré selon vos priorités.", "vues/tco.py"),
    ("3", "Négociation", "Leviers chiffrés pour chaque fournisseur, position de négociation, brouillon d'e-mail "
     "et note de décision en PDF.", "vues/negociation.py"),
]
for col, (num, titre, texte, page) in zip(st.columns(3, gap="medium"), etapes):
    with col:
        st.html(f'<div class="etape"><div class="num{"" if page else " inactif"}">{num}</div>'
                f'<div class="titre">{e(titre)}</div><div class="texte">{e(texte)}</div></div>')
        if page:
            st.page_link(page, label=f"Ouvrir l'étape {num}", icon=":material/arrow_forward:")

st.caption("Toutes les entreprises, tous les devis et toutes les données financières sont fictifs et ont été "
           "créés pour cette démonstration.")
