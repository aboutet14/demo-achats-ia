import streamlit as st

from lib.donnees import profil
from lib.style import bandeau, e

bandeau("Méthodologie", "Comment fonctionne cette démonstration",
        "Ce que fait l'IA, ce qui est calculé, et les limites de l'exercice.")

col1, col2 = st.columns(2, gap="medium")
with col1.container(border=True):
    st.markdown("#### Le rôle de l'IA")
    st.markdown(
        "- **Lire des documents hétérogènes** : devis PDF en français et en anglais, e-mail, pro forma en "
        "dollars. L'IA en extrait les mêmes informations dans un format commun.\n"
        "- **Repérer les pièges** : frais cachés, incoterm défavorable, minimum de commande, validité courte, "
        "clause d'indexation, acompte…\n"
        "- **Aider à rédiger** : conseils de négociation, phrases types et brouillons d'e-mail.\n\n"
        "L'acheteur garde la main : chaque valeur extraite est vérifiable et corrigeable, et les décisions "
        "reposent sur des calculs transparents."
    )
    st.caption("Mode démonstration : les extractions ont été réalisées par IA (Claude) puis enregistrées, pour que "
               "le site soit gratuit, instantané et sans risque de panne.")

with col2.container(border=True):
    st.markdown("#### Ce qui est calculé")
    st.markdown(
        "- **Coût complet (TCO)** : prix, outillage et emballage, qualification du fournisseur, transport et "
        "assurance selon l'incoterm, douane, coût ou gain de trésorerie (acompte, délai de paiement, escompte), "
        "risque de change, non-qualité, excédent imposé par le minimum de commande.\n"
        "- **Matrice de décision** : 5 critères notés sur 10 (coût, délai, qualité, risque fournisseur, "
        "paiement), pondérés par le visiteur.\n"
        "- **Négociation** : prix d'ouverture, objectif et limite pour chaque fournisseur ; leviers chiffrés en "
        "euros ; prix à partir duquel un concurrent passerait en tête."
    )

with st.container(border=True):
    st.markdown("#### Limites et usage réel")
    st.markdown(
        "- Toutes les entreprises, tous les devis et toutes les données financières sont **fictifs**.\n"
        "- Les hypothèses (transport, taux de financement, coût d'un défaut…) sont modifiables : dans un cas réel, "
        "elles viennent des données de l'entreprise.\n"
        "- Avec de vrais devis, l'outil fonctionnerait **en local ou sur l'infrastructure de l'entreprise**, "
        "jamais sur un site public, et dans le respect de sa politique d'usage de l'IA."
    )

auteur = profil()
if auteur.get("nom"):
    lien = f' · <a href="{e(auteur["linkedin"])}" target="_blank">Profil LinkedIn</a>' if auteur.get("linkedin") else ""
    st.html(f'<div class="reco"><div class="titre">À propos</div>'
            f'<div class="gagnant">{e(auteur["nom"])}</div>'
            f'<p>{e(auteur.get("titre", ""))}{lien}</p>'
            f'<p>Projet réalisé pour montrer comment l\'IA peut renforcer le métier d\'acheteur : plus de temps '
            f'pour l\'analyse et la négociation, moins pour la saisie.</p></div>')
