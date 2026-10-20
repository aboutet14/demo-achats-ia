"""Plan de négociation : leviers chiffrés à partir des écarts entre les offres."""
import copy
import re

from lib.conseils import conseil, deroule
from lib.tco import calculer_tco, noter, score_pondere

DELAI_PAIEMENT_CIBLE = 60  # jours date de facture : plafond légal en France (art. L441-10 du Code de commerce)
SEUIL_SOLVABILITE = 8  # note sur 20 en dessous de laquelle un fournisseur n'est pas une alternative crédible
INCOTERMS_RENDUS = ("DAP", "DPU", "DDP")
BAISSE_MAX_REALISTE = 0.20  # au-delà, une baisse de prix n'est pas un objectif crédible


def _prix(valeur, devise):
    texte = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} €" if devise == "EUR" else f"{texte} {devise}"


def _leviers(d, devis, besoin, fournisseurs, hyp, analyse):
    """Leviers d'un fournisseur. Les arguments ne citent jamais un concurrent par son nom."""
    r = analyse["resultats"][d["id"]]
    postes = r["postes"]
    hg, hf = hyp["generales"], hyp["par_fournisseur"][d["id"]]
    f = fournisseurs[d["id"]]
    autres = [x for x in devis if x["id"] != d["id"]]
    leviers = []

    def ajouter(titre, demande, argument, gain=0.0, nature="Coût", code=None):
        leviers.append({"titre": titre, "demande": demande, "argument": argument, "gain": gain, "nature": nature,
                        "code": code})

    if postes["Frais fixes (outillage, emballage)"] > 0:
        concurrent_inclut = any(sum(x["montant"] or 0 for x in a["frais_fixes"]) == 0 for a in autres)
        ajouter("Outillage et emballage inclus",
                "la prise en charge de l'outillage et de l'emballage",
                "Une offre concurrente inclut l'outillage dans son prix unitaire." if concurrent_inclut else
                "Ces frais sont amortis sur une seule commande : leur prise en charge, ou leur étalement sur les "
                "commandes suivantes, est un geste habituel pour gagner un nouveau client.",
                postes["Frais fixes (outillage, emballage)"], code="frais")

    logistique = postes["Transport et assurance"] + postes["Douane et formalités"]
    if d["incoterm"] not in INCOTERMS_RENDUS and logistique > 0:
        ajouter(f"Passer de {d['incoterm']} à DAP Lyon",
                "une livraison DAP à notre entrepôt de Lyon, à prix unitaire inchangé",
                f"En {d['incoterm']}, transport, assurance et formalités sont à notre charge, alors que d'autres "
                "offres sont livrées rendues entrepôt. Le fournisseur négocie aussi ses transports à l'année, "
                "souvent moins cher que nous pour un envoi ponctuel.",
                logistique, code="incoterm")

    if d["devise"] != "EUR":
        ajouter("Prix ferme en euros", "un prix ferme exprimé en euros",
                "La facturation en dollars nous fait porter le risque de change entre la commande et le paiement.",
                postes["Provision risque de change"], "Risque", code="devise")

    jours = r["jours_paiement_moyens"]
    if jours < DELAI_PAIEMENT_CIBLE:
        gain = r["montant_devis"] * hg["taux_financement_annuel"] * (DELAI_PAIEMENT_CIBLE - jours) / 365
        if d["acompte_pct"]:
            ajouter("Supprimer l'acompte", "la suppression de l'acompte et un paiement à 60 jours date de facture",
                    f"Payer {d['acompte_pct']:g} % à la commande et le solde avant expédition nous fait financer la "
                    "production et nous prive de tout moyen de pression en cas de défaut qualité.", gain, "Trésorerie",
                    code="paiement")
        else:
            ajouter("Paiement à 60 jours date de facture", "un paiement à 60 jours date de facture",
                    f"Le paiement actuel ({d['paiement_texte']}) est plus court que nos conditions standard "
                    "et que d'autres offres reçues.", gain, "Trésorerie", code="paiement")

    if d["quantite_minimum"] > besoin["quantite"]:
        ajouter("Lever le minimum de commande",
                f"une commande limitée à {besoin['quantite']:,} unités".replace(",", " "),
                f"Le minimum de {d['quantite_minimum']:,} unités nous ferait payer {r['excedent']:,} présentoirs "
                "personnalisés inutilisables après le lancement.".replace(",", " "),
                postes["Excédent non utilisé"], code="moq")

    tolerance = re.search(r"±\s*(\d+(?:,\d+)?)\s*%", d["tolerance_quantite"])
    if tolerance and float(tolerance.group(1).replace(",", ".")) > 1:
        ecart = float(tolerance.group(1).replace(",", ".")) - 1
        ajouter("Tolérance de quantité à ± 1 %", "une tolérance de quantité ramenée à ± 1 %",
                f"Avec {d['tolerance_quantite']}, on peut nous livrer et facturer des présentoirs en trop, "
                "inutilisables après le lancement. Gain indiqué : surfacturation maximale évitée.",
                ecart / 100 * postes["Achat (quantité utile)"], "Risque", code="tolerance")

    if "index" in d["revision_prix"].lower():
        ajouter("Prix ferme jusqu'à la livraison", "un prix ferme et non révisable jusqu'à la livraison",
                "La clause d'indexation nous fait porter le risque d'une hausse du carton. Gain indiqué : "
                "risque évité pour une hausse de 5 %.", 0.05 * postes["Achat (quantité utile)"], "Risque",
                code="indexation")

    if hf["taux_defaut_estime"] >= 0.015:
        gain = postes["Non-qualité estimée"] - besoin["quantite"] * 0.005 * hg["cout_par_defaut_qualite_eur"]
        ajouter("Clause qualité avec pénalités",
                "un engagement sur un taux de défaut ≤ 0,5 %, avec tri et remplacement à votre charge",
                "Pour une première commande, le risque qualité doit être porté par le fournisseur, pas par nous.",
                gain, "Qualité", code="qualite")

    if r["marge_jours"] < 0:
        ajouter("Livrer avant la date de besoin",
                f"une livraison au plus tard le {besoin['date_besoin'][8:]}/{besoin['date_besoin'][5:7]}",
                f"Avec le délai annoncé, la livraison arriverait le {r['livraison']:%d/%m}, soit "
                f"{-r['marge_jours']} jours après notre lancement : c'est une condition éliminatoire.",
                0, "Condition", code="delai")

    if f["note_solvabilite_sur_20"] < SEUIL_SOLVABILITE:
        ajouter("Sécuriser le risque fournisseur", "aucun acompte et un paiement après réception conforme",
                f"Santé financière fragile (note {f['note_solvabilite_sur_20']}/20) : il faut éviter toute avance "
                "de trésorerie et garder un fournisseur de secours.", 0, "Condition",
                code="solvabilite")

    if d["validite_jours"] <= 30:
        ajouter("Prolonger la validité de l'offre", "une validité de l'offre portée à 60 jours",
                f"{d['validite_jours']} jours ne suffisent pas pour valider le BAT et l'échantillon.", 0, "Condition",
                code="validite")

    return sorted(leviers, key=lambda l: l["gain"], reverse=True)


def _appliquer_leviers(d, hyp, leviers):
    """Offre et hypothèses telles qu'elles seraient si les leviers chiffrés étaient obtenus."""
    d2, hyp2 = copy.deepcopy(d), copy.deepcopy(hyp)
    codes = {l["code"] for l in leviers}
    if "frais" in codes:
        d2["frais_fixes"] = []
    if "incoterm" in codes:
        d2["incoterm"] = "DAP"
        hyp2["par_fournisseur"][d["id"]].update(transport_eur=0, taux_assurance_transport=0,
                                                 dedouanement_export_eur=0, dedouanement_import_eur=0)
    if "paiement" in codes:
        d2.update(acompte_pct=0, jours_paiement=DELAI_PAIEMENT_CIBLE)
    if "moq" in codes:
        d2["quantite_minimum"] = 0
    return d2, hyp2


def _scores_si_prix(d, prix, devis, besoin, fournisseurs, hyp, poids):
    modifies = [dict(d, prix_unitaire=prix) if x["id"] == d["id"] else x for x in devis]
    resultats = {x["id"]: calculer_tco(x, besoin, hyp) for x in modifies}
    notes = noter(modifies, resultats, fournisseurs, hyp)
    return {i: score_pondere(notes[i], poids) for i in notes}


def _position(d, devis, besoin, fournisseurs, hyp, analyse, poids, leviers):
    """Prix d'ouverture, objectif et limite pour un fournisseur."""
    r = analyse["resultats"][d["id"]]
    prix = d["prix_unitaire"]
    taux = r["prix_affiche_eur"] / prix
    gagnant = analyse["gagnant"]
    position = {"prix": prix, "devise": d["devise"], "ouverture": None, "objectif": None, "limite": None}

    if r["marge_jours"] < 0:
        return {**position, "role": "bloque",
                "explication": f"Livraison prévue {-r['marge_jours']} jours après la date de besoin : le délai doit "
                               "être réglé avant toute discussion de prix."}

    if d["id"] == gagnant:
        credibles = [x["id"] for x in devis if x["id"] != d["id"]
                     and analyse["resultats"][x["id"]]["marge_jours"] >= 0
                     and fournisseurs[x["id"]]["note_solvabilite_sur_20"] >= SEUIL_SOLVABILITE]
        gains = sum(l["gain"] for l in leviers if l["nature"] in ("Coût", "Trésorerie"))
        tco_apres = r["total"] - gains
        reference = min(credibles, key=lambda i: analyse["resultats"][i]["total"]) if credibles else None
        tco_ref = analyse["resultats"][reference]["total"] if reference else tco_apres
        equilibre = prix - max(0.0, tco_apres - tco_ref) / besoin["quantite"] / taux
        if equilibre < prix * 0.97:
            objectif = min(prix * 0.97, (prix + equilibre) / 2)
            explication = (f"À {_prix(equilibre, d['devise'])}, l'offre égalerait en coût complet la meilleure "
                           "alternative crédible (prix d'ouverture). Elle reste recommandée à son prix actuel grâce à "
                           "ses autres atouts : le prix actuel est donc la limite.")
        else:
            equilibre, objectif = prix * 0.93, prix * 0.97
            explication = ("L'offre est déjà la plus compétitive en coût complet : on vise une remise d'usage "
                           "pour conclure.")
        return {**position, "role": "gagnant", "ouverture": equilibre, "objectif": objectif, "limite": prix,
                "explication": explication}

    # Fournisseur challenger : une fois les leviers obtenus, à quel prix passerait-il en tête du classement ?
    d_apres, hyp_apres = _appliquer_leviers(d, hyp, leviers)

    def passe_devant(p):
        scores = _scores_si_prix(d_apres, p, devis, besoin, fournisseurs, hyp_apres, poids)
        return scores[d["id"]] > scores[gagnant]

    if passe_devant(prix):
        return {**position, "role": "challenger", "ouverture": prix * 0.93, "objectif": prix * 0.97,
                "limite": prix,
                "explication": "Si les conditions demandées sont obtenues, cette offre passe en tête même à prix "
                               "inchangé : la négociation porte d'abord sur les conditions, puis sur une remise "
                               "d'usage."}
    plancher = prix * (1 - BAISSE_MAX_REALISTE)
    if not passe_devant(plancher):
        return {**position, "role": "comparaison",
                "explication": f"Même avec les conditions demandées, il faudrait une baisse de prix de plus de "
                               f"{BAISSE_MAX_REALISTE:.0%} pour passer en tête : peu réaliste. L'offre sert surtout "
                               "de point de comparaison dans la négociation."}
    bas, haut = plancher, prix
    for _ in range(30):
        milieu = (bas + haut) / 2
        bas, haut = (milieu, haut) if passe_devant(milieu) else (bas, milieu)
    return {**position, "role": "challenger", "ouverture": bas * 0.95, "objectif": bas, "limite": bas,
            "explication": f"Avec les conditions demandées et un prix sous {_prix(bas, d['devise'])}, cette offre "
                           "passerait en tête du classement : c'est le levier de mise en concurrence face à l'offre "
                           "recommandée."}


def _email(d, besoin, plan_f):
    position, leviers = plan_f["position"], plan_f["leviers"]
    demandes = [l["demande"] for l in leviers if l["code"] != "prix"]
    if position["ouverture"]:
        # On annonce le prix d'ouverture (ancrage) : l'objectif et la limite restent internes.
        baisse = 1 - position["ouverture"] / position["prix"]
        demandes.insert(0, f"un prix unitaire de {_prix(position['ouverture'], position['devise'])} "
                           f"(-{baisse:.1%})".replace(".", ","))
    intro = {
        "gagnant": "Votre offre se distingue par sa fiabilité, mais elle se situe nettement au-dessus de la "
                   "meilleure offre reçue en coût complet.",
        "challenger": "Votre offre est compétitive, mais elle n'est pas aujourd'hui la mieux placée.",
        "comparaison": "Votre offre présente des atouts, mais elle reste en retrait de la meilleure offre reçue.",
        "bloque": "En l'état, votre offre ne peut pas être retenue.",
    }[position["role"]]
    lignes = "\n".join(f"- {x[0].upper()}{x[1:]}" for x in demandes)
    return (f"Objet : Consultation {besoin.get('reference_consultation', '')} – suite à votre offre {d['reference']}\n\n"
            "Bonjour,\n\n"
            f"Merci pour votre offre du {d['date'][8:]}/{d['date'][5:7]}/{d['date'][:4]}. Nous avons comparé "
            "l'ensemble des propositions reçues en coût complet : prix, logistique, conditions de paiement, "
            f"qualité et délai.\n\n{intro} Pour poursuivre, nous vous demandons :\n{lignes}\n\n"
            "Merci de nous adresser une offre révisée sous 7 jours.\n\n"
            "Cordialement,\nService Achats")


def _contexte(d, devis, besoin, fournisseurs, analyse, position):
    """Chiffres du dossier insérés dans les conseils de négociation."""
    res = analyse["resultats"]
    r = res[d["id"]]
    credibles = [x["id"] for x in devis if x["id"] != d["id"] and res[x["id"]]["marge_jours"] >= 0
                 and fournisseurs[x["id"]]["note_solvabilite_sur_20"] >= SEUIL_SOLVABILITE]
    reference = min((res[i]["total"] for i in credibles), default=r["total"])
    euros = lambda v: f"{v:,.0f}".replace(",", " ") + " €"
    return {
        "ecart_pct": f"{(r['total'] - reference) / reference:+.0%}".replace(".", ","),
        "ouverture": _prix(position["ouverture"], d["devise"]) if position["ouverture"] else "…",
        "frais": euros(r["postes"]["Frais fixes (outillage, emballage)"]),
        "incoterm": d["incoterm"],
        "logistique_u": _prix((r["postes"]["Transport et assurance"] + r["postes"]["Douane et formalités"])
                              / besoin["quantite"], "EUR"),
        "besoin": f"{besoin['quantite']:,}".replace(",", " "),
        "excedent": f"{r['excedent']:,}".replace(",", " "),
        "date_besoin": f"{besoin['date_besoin'][8:]}/{besoin['date_besoin'][5:7]}/{besoin['date_besoin'][:4]}",
        "validite": d["validite_jours"],
    }


def preparer_plan(devis, besoin, fournisseurs, hyp, analyse, poids):
    plan = {}
    for d in devis:
        leviers = _leviers(d, devis, besoin, fournisseurs, hyp, analyse)
        position = _position(d, devis, besoin, fournisseurs, hyp, analyse, poids, leviers)
        if position["objectif"]:
            r = analyse["resultats"][d["id"]]
            gain = (position["prix"] - position["objectif"]) * r["qte_commandee"] * r["prix_affiche_eur"] / d["prix_unitaire"]
            leviers.append({"titre": "Baisse du prix unitaire", "demande": "", "nature": "Prix", "code": "prix",
                            "gain": gain, "argument": position["explication"]})
            leviers.sort(key=lambda l: l["gain"], reverse=True)
        contexte = _contexte(d, devis, besoin, fournisseurs, analyse, position)
        for l in leviers:
            l["conseil"] = conseil(l, position["role"], d["acompte_pct"], contexte)
        plan[d["id"]] = {"leviers": leviers, "position": position, "deroule": deroule(position["role"], contexte)}
        plan[d["id"]]["email"] = _email(d, besoin, plan[d["id"]])
    return plan


def economie_potentielle(d, analyse, plan_f):
    """Économie sur le coût complet si l'objectif de prix et les leviers chiffrés sont obtenus."""
    r, position = analyse["resultats"][d["id"]], plan_f["position"]
    taux = r["prix_affiche_eur"] / d["prix_unitaire"]
    prix = (position["prix"] - position["objectif"]) * r["qte_commandee"] * taux if position["objectif"] else 0
    return prix + sum(l["gain"] for l in plan_f["leviers"] if l["nature"] in ("Coût", "Trésorerie", "Qualité"))
