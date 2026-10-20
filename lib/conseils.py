"""Conseils de négociation : comment aborder chaque levier avec le fournisseur.

Les textes entre accolades ({ouverture}, {besoin}…) sont remplacés par les chiffres du dossier.
"""

# Déroulé conseillé de l'entretien selon la position du fournisseur.
DEROULES = {
    "gagnant": [
        "Valoriser la relation : qualité, fiabilité, historique. Le fournisseur doit sentir qu'il est en position "
        "de gagner, pas qu'il a déjà gagné.",
        "Poser le constat chiffré en coût complet, sans citer de concurrent : « l'écart est de {ecart_pct} ».",
        "Annoncer le prix d'ouverture comme la conséquence de l'analyse, puis se taire et laisser le fournisseur "
        "réagir en premier.",
        "Ne concéder qu'en échange d'une contrepartie (donnant-donnant), en gardant l'objectif et la limite pour soi.",
        "Conclure par écrit : offre révisée, prix ferme, date de validité.",
    ],
    "challenger": [
        "Montrer un intérêt réel : le fournisseur est dans la short-list et a une vraie chance.",
        "Traiter d'abord les conditions (livraison, outillage, paiement) : une fois alignées, l'effort de prix "
        "demandé paraît modeste.",
        "Annoncer ensuite le prix d'ouverture, en coût rendu Lyon.",
        "Fixer les prochaines étapes concrètes (échantillon, audit, date de décision) pour entretenir la dynamique.",
    ],
    "comparaison": [
        "Garder le fournisseur dans la consultation : son offre sert de point de comparaison.",
        "Obtenir l'alignement des conditions, sans investir trop de temps sur le prix.",
        "Rester transparent sur le calendrier de décision.",
    ],
    "bloque": [
        "Poser d'entrée la condition bloquante : inutile de négocier un prix pour une offre qui ne peut pas être "
        "retenue.",
        "Si la condition est levée par écrit, traiter les autres leviers dans l'ordre de leur gain.",
        "Sinon, remercier et clore proprement : le fournisseur pourra être consulté sur un prochain dossier.",
    ],
}

# Conseil par levier. « prix » a une variante selon la position du fournisseur.
CONSEILS = {
    ("prix", "gagnant"): {
        "technique": "Ancrage argumenté, puis concessions conditionnelles",
        "comment": "Ne jamais demander « un effort » sans justification. Commencer par reconnaître les atouts du "
                   "fournisseur, puis présenter l'écart en coût complet comme un problème à résoudre ensemble. "
                   "Le prix d'ouverture découle de l'analyse : on ne l'exige pas, on l'explique.",
        "phrase": "Votre offre reste notre référence sur la qualité et le délai, et nous souhaitons continuer avec "
                  "vous. Mais en coût complet, l'écart avec les autres offres reçues est de {ecart_pct} : je ne "
                  "peux pas le défendre en interne en l'état. Pour que je puisse vous retenir, il faudrait se "
                  "rapprocher de {ouverture}. Qu'est-ce qui est envisageable de votre côté ?",
        "objection": "« Nos prix sont déjà serrés, la matière a augmenté. »",
        "reponse": "Demander la décomposition du prix (carton, impression, main-d'œuvre, marge) pour discuter poste "
                   "par poste, et proposer des pistes qui baissent ses coûts plutôt que sa marge : spécification du "
                   "carton, regroupement des livraisons, délai plus souple.",
        "contrepartie": "Visibilité sur les prochains lancements, accord-cadre annuel, BAT validé sous 48 h.",
    },
    ("prix", "challenger"): {
        "technique": "Mise en concurrence sans révéler les offres",
        "comment": "Le fournisseur doit comprendre qu'il peut gagner, à condition de bouger. Commencer par les "
                   "conditions, puis le prix : après l'alignement des conditions, la baisse demandée paraît "
                   "raisonnable.",
        "phrase": "Votre offre nous intéresse et vous êtes dans la short-list. Pour passer devant, il faut aligner "
                  "vos conditions sur ce que nous recevons par ailleurs, et un prix autour de {ouverture}. Si vous "
                  "pouvez vous engager là-dessus, nous organisons rapidement l'échantillon.",
        "objection": "« Quel prix avez-vous reçu ailleurs ? »",
        "reponse": "Ne jamais communiquer le prix d'un concurrent (confidentialité et loyauté de la consultation). "
                   "Répondre en coût complet : « Je compare en coût rendu Lyon, conditions comprises, et sur cette "
                   "base vous êtes aujourd'hui au-dessus. »",
        "contrepartie": "Un premier marché avec un nouveau client, et des volumes récurrents si la première commande "
                        "est réussie.",
    },
    "frais": {
        "technique": "Effet « premier marché »",
        "comment": "Présenter l'outillage comme l'investissement du fournisseur pour gagner un nouveau client, "
                   "amortissable sur les commandes suivantes. Prévoir une solution de repli s'il refuse.",
        "phrase": "L'outillage pèse {frais} sur une seule commande. Pour un premier marché, nous attendons qu'il "
                  "soit inclus, ou au minimum amorti sur les prochaines commandes.",
        "objection": "« L'outillage est spécifique à votre projet. »",
        "reponse": "Demander alors la propriété de la forme de découpe (réutilisable ailleurs) et sa gratuité en cas "
                   "de nouvelle commande.",
        "contrepartie": "Réutiliser le même format sur les prochains lancements.",
    },
    "incoterm": {
        "technique": "Comparer à périmètre égal",
        "comment": "Ce n'est pas une demande de remise mais une mise à niveau du périmètre : toutes les offres sont "
                   "comparées rendues entrepôt. Le fournisseur a souvent des tarifs de transport annuels plus bas "
                   "que l'acheteur pour un envoi ponctuel.",
        "phrase": "Toutes les offres sont comparées rendues à notre entrepôt de Lyon. En {incoterm}, votre offre "
                  "n'est pas comparable : pouvez-vous nous la chiffrer en DAP Lyon ?",
        "objection": "« Le transport n'est pas notre métier. »",
        "reponse": "Proposer qu'il passe par son transporteur habituel, ou rester en {incoterm} si le prix unitaire "
                   "baisse d'autant (environ {logistique_u} par présentoir).",
        "contrepartie": "Souplesse sur le créneau de livraison, un seul envoi groupé.",
    },
    "devise": {
        "technique": "Partage du risque",
        "comment": "Le risque de change n'est pas une marge : proposer de le partager ou de figer un taux à la "
                   "commande, plutôt que de le subir.",
        "phrase": "Nous travaillons en euros. Pouvez-vous nous proposer un prix ferme en euros, ou un taux de "
                  "change fixé à la date de commande ?",
        "objection": "« Nos coûts sont en dollars. »",
        "reponse": "Proposer un « tunnel » : le prix n'est révisé que si le taux sort d'une fourchette de ± 3 %.",
        "contrepartie": "Un paiement rapide après livraison pour réduire son exposition.",
    },
    ("paiement", "acompte"): {
        "technique": "Sécurité contre sécurité",
        "comment": "Un acompte élevé fait financer la production par l'acheteur et lui retire tout moyen de "
                   "pression en cas de défaut. Proposer des garanties alternatives plutôt que de refuser sèchement.",
        "phrase": "Sur une première commande, nous ne pouvons pas payer la totalité avant la livraison. Nous "
                  "proposons 60 jours date de facture ; si un acompte est indispensable, il devra être limité et "
                  "couvert par une garantie bancaire.",
        "objection": "« C'est notre condition standard à l'export. »",
        "reponse": "Proposer un crédit documentaire ou un paiement contre documents d'expédition, avec une "
                   "inspection avant départ.",
        "contrepartie": "Des délais de paiement plus courts sur les commandes suivantes, une fois la confiance "
                        "établie.",
    },
    "paiement": {
        "technique": "Alignement sur la norme",
        "comment": "Présenter 60 jours date de facture comme la norme interne (et le plafond légal en France), pas "
                   "comme une faveur. À aborder en fin d'entretien, une fois le prix stabilisé.",
        "phrase": "Nos conditions standard sont à 60 jours date de facture. Pouvez-vous vous aligner ?",
        "objection": "« Notre trésorerie ne le permet pas. »",
        "reponse": "Proposer un escompte pour paiement anticipé : il choisit entre sa trésorerie et sa marge.",
        "contrepartie": "Respect strict des échéances.",
    },
    "moq": {
        "technique": "Revenir au besoin réel",
        "comment": "Le minimum de commande sert la productivité du fournisseur, pas le besoin de l'acheteur. "
                   "Chercher une solution qui préserve sa ligne de production sans payer l'excédent.",
        "phrase": "Notre besoin est de {besoin} présentoirs personnalisés : les {excedent} en plus seraient "
                  "détruits après le lancement. Pouvez-vous produire {besoin} unités, quitte à regrouper la "
                  "production avec une autre série ?",
        "objection": "« En dessous du minimum, le prix unitaire augmente. »",
        "reponse": "Demander le prix pour {besoin} unités et comparer : la hausse est souvent inférieure au coût "
                   "de l'excédent.",
        "contrepartie": "Un planning souple, pour caler la production sur un creux de charge.",
    },
    "tolerance": {
        "technique": "Clause technique, pas commerciale",
        "comment": "Aborder le sujet comme un point contractuel standard, en fin de discussion : il passe plus "
                   "facilement une fois le prix arrêté.",
        "phrase": "Sur des présentoirs personnalisés, une surlivraison est perdue pour nous : nous facturons au "
                  "réel, avec une tolérance de ± 1 %.",
        "objection": "« La gâche est inévitable en impression. »",
        "reponse": "Accepter la gâche, mais sans la facturer : le surplus reste à la charge du fournisseur.",
        "contrepartie": "Aucune nécessaire : c'est une pratique courante.",
    },
    "indexation": {
        "technique": "Prix ferme contre décision rapide",
        "comment": "Une clause d'indexation fait porter le risque matière à l'acheteur. L'échanger contre ce qui a "
                   "de la valeur pour le fournisseur : une décision rapide.",
        "phrase": "Si nous confirmons la commande sous 10 jours, pouvez-vous garantir un prix ferme jusqu'à la "
                  "livraison ?",
        "objection": "« Le prix du carton est trop volatil. »",
        "reponse": "Accepter une indexation symétrique (à la hausse comme à la baisse), sur un indice publié, avec "
                   "un seuil de déclenchement.",
        "contrepartie": "Une confirmation de commande rapide.",
    },
    "qualite": {
        "technique": "Engagement de résultat",
        "comment": "Pour un nouveau fournisseur, faire porter le risque qualité par celui qui le maîtrise. Le "
                   "présenter comme une condition de référencement, pas comme de la défiance.",
        "phrase": "Pour référencer un nouveau fournisseur, nous demandons un engagement : taux de défaut "
                  "≤ 0,5 %, et au-delà, tri et remplacement à votre charge.",
        "objection": "« Nous faisons déjà un contrôle qualité final. »",
        "reponse": "Demander le rapport de contrôle à chaque livraison, et une inspection indépendante avant "
                   "expédition pour la première commande.",
        "contrepartie": "Des volumes récurrents si les objectifs qualité sont tenus.",
    },
    "delai": {
        "technique": "Condition éliminatoire posée d'entrée",
        "comment": "Poser le délai comme un préalable, avant toute discussion de prix.",
        "phrase": "Avant d'aller plus loin : notre lancement est prévu le {date_besoin}. Pouvez-vous vous engager "
                  "par écrit à livrer avant cette date, avec des pénalités de retard ?",
        "objection": "« Nos délais sont incompressibles. »",
        "reponse": "Explorer un BAT anticipé, une production en deux lots ou un transport express, et chiffrer le "
                   "surcoût.",
        "contrepartie": "Une validation du BAT sous 24 h de notre côté.",
    },
    "solvabilite": {
        "technique": "Sécuriser sans fermer la porte",
        "comment": "Ne jamais évoquer directement la santé financière du fournisseur (sujet sensible) : demander "
                   "des conditions qui protègent naturellement l'acheteur.",
        "phrase": "Pour une première collaboration, notre procédure prévoit un paiement après réception "
                  "conforme, sans acompte.",
        "objection": "« Nous avons besoin d'un acompte pour acheter la matière. »",
        "reponse": "Refuser l'acompte, ou le limiter et l'adosser à une garantie bancaire, et garder un fournisseur "
                   "de secours prêt.",
        "contrepartie": "Un paiement rapide à réception, avec escompte.",
    },
    "validite": {
        "technique": "Résister à l'urgence artificielle",
        "comment": "Une validité très courte est souvent une technique de pression. Ne pas décider dans "
                   "l'urgence : une prolongation est rarement refusée.",
        "phrase": "Notre processus de validation (BAT, échantillon) prend plus de {validite} jours. Pouvez-vous "
                  "prolonger votre offre à 60 jours ?",
        "objection": "« Les prix matière vont augmenter. »",
        "reponse": "Accepter une prolongation plus courte, en échange d'une date de décision ferme de notre côté.",
        "contrepartie": "Une date de décision engagée.",
    },
}


class _Contexte(dict):
    def __missing__(self, cle):
        return "…"


def conseil(levier, role, acompte, contexte):
    """Conseil du levier, avec les chiffres du dossier."""
    code = levier["code"]
    modele = (CONSEILS.get((code, role)) or CONSEILS.get((code, "acompte" if acompte else None))
              or CONSEILS.get(code) or CONSEILS.get(("prix", "challenger")))
    return {cle: texte.format_map(_Contexte(contexte)) for cle, texte in modele.items()}


def deroule(role, contexte):
    return [etape.format_map(_Contexte(contexte)) for etape in DEROULES[role]]
