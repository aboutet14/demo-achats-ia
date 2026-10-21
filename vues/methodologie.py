import pandas as pd
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
        "euros ; prix à partir duquel un concurrent passerait en tête.\n"
        "- **Suivi fournisseur** : gain de négociation, indicateurs mensuels (délai, service, qualité, prix "
        "facturé), scorecard pondérée et alertes. Détail ci-dessous."
    )

with st.container(border=True):
    st.markdown("#### Le suivi du fournisseur retenu (KPI)")
    st.markdown(
        "Un achat ne s'arrête pas à la signature : la page *Suivi fournisseur* vérifie que le fournisseur "
        "recommandé tient ses engagements. Elle reprend automatiquement l'offre gagnante de l'étape 2, et le prix "
        "objectif de l'étape 3 comme prix signé (modifiable)."
    )
    st.markdown("**Gain de la négociation**")
    st.markdown(
        "- **Gain de négociation** : (prix du devis − prix signé) × quantité.\n"
        "- **Économie vs marché** : (prix moyen des offres reçues − prix signé) × quantité.\n"
        "- **Dépense engagée** : prix signé × quantité."
    )
    st.markdown("**Indicateurs mensuels**, calculés à partir du tableau de suivi")
    st.table(pd.DataFrame({
        "Indicateur": ["OTD (ponctualité)", "Taux de service", "Qualité", "Surfacturation"],
        "Ce qu'il mesure": ["Les livraisons arrivent-elles à la date confirmée ?",
                            "Les commandes sont-elles livrées sans manquant ?",
                            "Les produits reçus sont-ils conformes ?",
                            "Le prix facturé respecte-t-il le prix signé ?"],
        "Calcul": ["Commandes livrées à l'heure ÷ commandes",
                   "Commandes livrées complètes ÷ commandes",
                   "Quantités non conformes ÷ quantités reçues",
                   "Écart maximal entre prix facturé et prix signé"],
        "Objectif par défaut": ["≥ 95 %", "≥ 98 %", "≤ 0,5 %", "0 %"],
    }).set_index("Indicateur"))
    st.markdown("**Scorecard et alertes**")
    st.markdown(
        "- Chaque critère reçoit une note sur 100 : délai et service selon l'atteinte de leur objectif ; qualité "
        "à 100 sans défaut et à 50 au maximum contractuel ; prix facturé : −20 points par % de surfacturation.\n"
        "- Le **score global** est la moyenne pondérée de ces notes (pondération réglable par le visiteur) : "
        "**85 et plus** = fournisseur performant, **70 à 84** = sous surveillance avec plan d'action, "
        "**moins de 70** = escalade et re-sourcing à envisager.\n"
        "- Des **alertes** signalent automatiquement, mois par mois, les retards, les manquants, la non-qualité "
        "et les factures au-dessus du prix signé : c'est la base de la revue de performance avec le fournisseur."
    )
    st.caption("Ici, ces indicateurs sont des calculs, sans IA. Dans un cas réel, les données viendraient de l'ERP "
               "(commandes, réceptions, contrôles qualité, factures) au lieu d'être saisies dans le tableau.")

with st.container(border=True):
    st.markdown("#### Limites et usage réel")
    st.markdown(
        "- Toutes les entreprises, tous les devis, toutes les données financières et les données de suivi "
        "fournisseur sont **fictifs**.\n"
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
