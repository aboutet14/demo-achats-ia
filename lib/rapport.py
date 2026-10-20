"""Export PDF : note de décision achat (synthèse, coût complet, matrice, plan de négociation)."""
import html
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from lib.negociation import economie_potentielle
from lib.tco import COURTS, CRITERES

MARINE = colors.HexColor("#0F2A47")
BLEU = colors.HexColor("#1F5A96")
GRIS = colors.HexColor("#5B6B80")
FOND = colors.HexColor("#EEF3F9")
VERT = colors.HexColor("#1F8A5B")

# Caractères absents des polices PDF standard : on les remplace.
REMPLACEMENTS = {"−": "-", "≤": "<=", "≥": ">=", "≈": "env.", "→": "->", "★": "", "…": "...", " ": " "}

styles = getSampleStyleSheet()
TITRE = styles["Title"].clone("titre", fontSize=19, leading=23, alignment=0, textColor=MARINE, spaceAfter=2)
H2 = styles["Heading2"].clone("h2", fontSize=13, leading=16, textColor=BLEU, spaceBefore=12, spaceAfter=6)
H3 = styles["Heading3"].clone("h3", fontSize=11, leading=14, textColor=MARINE, spaceBefore=8, spaceAfter=4)
TEXTE = styles["Normal"].clone("texte", fontSize=9.5, leading=13)
PETIT = styles["Normal"].clone("petit", fontSize=8, leading=10.5, textColor=GRIS)
CELLULE = styles["Normal"].clone("cellule", fontSize=8.5, leading=10.5)


def _t(texte):
    texte = str(texte)
    for a, b in REMPLACEMENTS.items():
        texte = texte.replace(a, b)
    return texte


def _p(texte, style=TEXTE, echapper=True):
    texte = _t(texte)
    return Paragraph(html.escape(texte) if echapper else texte, style)


def _eur(valeur, decimales=0):
    texte = f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return f"{texte} €"


def _prix(valeur, devise):
    texte = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} €" if devise == "EUR" else f"{texte} {devise}"


def _tableau(lignes, largeurs, aligner_droite_a_partir_de=1):
    contenu = [[_p(c, CELLULE) if isinstance(c, str) else c for c in ligne] for ligne in lignes]
    t = Table(contenu, colWidths=largeurs, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FOND), ("TEXTCOLOR", (0, 0), (-1, 0), MARINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#DCE3EC")),
        ("ALIGN", (aligner_droite_a_partir_de, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def generer_pdf(besoin, devis, fournisseurs, analyse, poids, plan, auteur):
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(tampon, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm,
                            bottomMargin=18 * mm, title="Note de décision achat", author=auteur.get("nom", ""))
    largeur = A4[0] - 32 * mm
    res, scores = analyse["resultats"], analyse["scores"]
    par_id = {d["id"]: d for d in devis}
    nom = lambda i: fournisseurs[i]["nom"]
    el = []

    el += [_p("Note de décision achat", TITRE),
           _p(f"{besoin['titre']} · {besoin['acheteur']} · consultation {besoin.get('reference_consultation', '')}",
              PETIT),
           _p(f"Éditée le {date.today():%d/%m/%Y}" + (f" · Préparée par {auteur['nom']}" if auteur.get("nom") else "")
              + " · Démonstration : toutes les entreprises et données sont fictives.", PETIT),
           Spacer(1, 8)]

    # 1. Synthèse
    el.append(_p("1. Synthèse et recommandation", H2))
    gagnant = analyse["gagnant"]
    if gagnant:
        d = par_id[gagnant]
        eco = economie_potentielle(d, analyse, plan[gagnant])
        ecart = res[gagnant]["total"] - res[analyse["moins_cher_tco"]]["total"]
        lignes = [f"<b>Fournisseur recommandé : {html.escape(nom(gagnant))}</b> "
                  f"(score {scores[gagnant]:.2f}/10)".replace(".", ","),
                  f"Besoin : {besoin['quantite']:,} {html.escape(besoin['unite'])}, livraison au plus tard le "
                  f"{besoin['date_besoin'][8:]}/{besoin['date_besoin'][5:7]}/{besoin['date_besoin'][:4]}."
                  .replace(",", " ", 1),
                  f"Coût complet de l'offre recommandée : <b>{_eur(res[gagnant]['total'])}</b>, soit "
                  f"{_eur(res[gagnant]['unitaire'], 2)} par unité."]
        if gagnant != analyse["moins_cher_tco"]:
            lignes.append(f"Ce n'est pas l'offre la moins chère en coût complet (+{_eur(ecart)} face à "
                          f"{html.escape(nom(analyse['moins_cher_tco']))}) : cet écart est la base de la négociation.")
        lignes.append(f"Économie visée par la négociation : <b>{_eur(eco)}</b> sur le coût complet.")
        el += [_p(l, TEXTE, echapper=False) for l in lignes]

    # 2. Coût complet
    el.append(_p("2. Comparaison en coût complet (TCO)", H2))
    lignes = [["Fournisseur", "Prix affiché", "Coût complet / unité", "Coût complet total", "Livraison", "Score"]]
    for d in devis:
        r = res[d["id"]]
        lignes.append([f"{nom(d['id'])} ({d['pays']})", _eur(r["prix_affiche_eur"], 2), _eur(r["unitaire"], 2),
                       _eur(r["total"]), f"{r['livraison']:%d/%m/%Y}" + (" (retard)" if r["marge_jours"] < 0 else ""),
                       "Éliminé" if scores[d["id"]] is None else f"{scores[d['id']]:.2f}".replace(".", ",")])
    el.append(_tableau(lignes, [largeur * x for x in (0.30, 0.13, 0.16, 0.16, 0.14, 0.11)]))
    el.append(Spacer(1, 4))
    el.append(_p("Le coût complet inclut le prix, les frais fixes, la qualification du fournisseur, le transport, la "
                 "douane, le coût ou le gain de trésorerie, le risque de change, la non-qualité et l'excédent.", PETIT))

    # 3. Matrice
    el.append(_p("3. Matrice de décision pondérée", H2))
    total = sum(poids.values()) or 1
    el.append(_p("Pondération : " + " · ".join(f"{CRITERES[c]} {poids[c] / total:.0%}" for c in CRITERES), TEXTE))
    el.append(Spacer(1, 4))
    lignes = [["Rang", "Fournisseur"] + [COURTS[c] for c in CRITERES] + ["Score / 10"]]
    ordre = analyse["classement"] + [i for i in scores if scores[i] is None]
    for i in ordre:
        rang = str(analyse["classement"].index(i) + 1) if i in analyse["classement"] else "Éliminé"
        lignes.append([rang, nom(i)] + [f"{analyse['notes'][i][c]:.1f}".replace(".", ",") for c in CRITERES]
                      + ["-" if scores[i] is None else f"{scores[i]:.2f}".replace(".", ",")])
    el.append(_tableau(lignes, [largeur * x for x in (0.08, 0.28, 0.1, 0.1, 0.1, 0.1, 0.11, 0.13)], 2))

    # 4. Plan de négociation
    el.append(_p("4. Plan de négociation", H2))
    for i in ordre:
        d, pf = par_id[i], plan[i]
        pos = pf["position"]
        bloc = [_p(f"{nom(i)} ({d['pays']})", H3)]
        if pos["objectif"]:
            bloc.append(_p(f"Prix actuel {_prix(pos['prix'], pos['devise'])} · ouverture "
                           f"{_prix(pos['ouverture'], pos['devise'])} · objectif {_prix(pos['objectif'], pos['devise'])}"
                           f" · limite {_prix(pos['limite'], pos['devise'])}", TEXTE))
        bloc.append(_p(pos["explication"], PETIT))
        if pf["leviers"]:
            lignes = [["Levier", "Ce que l'on demande", "Gain estimé"]]
            lignes += [[l["titre"], l["demande"] or f"annoncer {_prix(pos['ouverture'], pos['devise'])} (ouverture) "
                                                    f"pour obtenir {_prix(pos['objectif'], pos['devise'])} (objectif)",
                        _eur(l["gain"]) if l["gain"] else l["nature"]] for l in pf["leviers"]]
            bloc += [Spacer(1, 3), _tableau(lignes, [largeur * x for x in (0.30, 0.52, 0.18)], 2)]
        el.append(KeepTogether(bloc))

    def pied(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(16 * mm, 10 * mm, _t("Achats × IA · démonstration · données fictives"))
        canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(el, onFirstPage=pied, onLaterPages=pied)
    return tampon.getvalue()
