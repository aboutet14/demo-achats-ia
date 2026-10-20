"""Génère les devis PDF factices du scénario « présentoirs PLV ».

Lancement : .venv/bin/python outils/generer_devis.py
"""
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DOSSIER = Path(__file__).resolve().parent.parent / "scenarios" / "presentoirs_plv" / "devis"
MENTION_FICTIF = (
    "Document fictif créé pour une démonstration – fictitious document for demonstration purposes. "
    "Toute ressemblance avec une entreprise existante serait fortuite."
)

styles = getSampleStyleSheet()
NORMAL = styles["Normal"]
PETIT = styles["Normal"].clone("petit", fontSize=8, leading=10, textColor=colors.grey)
TITRE = styles["Title"].clone("titre", alignment=0, fontSize=16)


def p(texte, style=NORMAL):
    return Paragraph(texte, style)


def creer_devis(fichier, couleur, emetteur, client, titre, infos, entetes, lignes, totaux, conditions, signature):
    """Construit un devis : en-tête émetteur/client, tableau des lignes, totaux, conditions."""
    doc = SimpleDocTemplate(str(DOSSIER / fichier), pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    largeur = A4[0] - 36 * mm
    elements = []

    bandeau = Table([[p(f"<font color='white' size=14><b>{emetteur[0]}</b></font>")]], colWidths=[largeur])
    bandeau.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), couleur),
                                 ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    elements += [bandeau, Spacer(1, 6)]

    adresses = Table([[p("<br/>".join(emetteur[1:])), p("<br/>".join(client))]], colWidths=[largeur / 2] * 2)
    adresses.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("BOX", (1, 0), (1, 0), 0.5, colors.grey)]))
    elements += [adresses, Spacer(1, 10), p(titre, TITRE), p("<br/>".join(infos)), Spacer(1, 10)]

    tableau = Table([entetes] + [[p(c) if i == 0 else c for i, c in enumerate(l)] for l in lignes],
                    colWidths=[largeur * 0.48, largeur * 0.10, largeur * 0.20, largeur * 0.22])
    tableau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), couleur), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
    ]))
    elements += [tableau, Spacer(1, 6)]

    bloc_totaux = Table(totaux, colWidths=[largeur * 0.80, largeur * 0.20])
    bloc_totaux.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                                     ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                                     ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black)]))
    elements += [bloc_totaux, Spacer(1, 12)]

    elements += [p(f"<b>{conditions[0]}</b>")] + [p(f"• {c}") for c in conditions[1:]]
    elements += [Spacer(1, 14), p(signature), Spacer(1, 20), p(MENTION_FICTIF, PETIT)]
    doc.build(elements)


def devis_cartonnages_du_rhone():
    creer_devis(
        "A_Cartonnages_du_Rhone.pdf", colors.HexColor("#1F4E79"),
        ["CARTONNAGES DU RHÔNE", "Cartonnages du Rhône SAS", "145 rue des Ateliers",
         "69400 Villefranche-sur-Saône – France", "Tél. +33 4 00 00 00 00"],
        ["<b>Orvalis Cosmétiques</b>", "Service Achats", "Livraison : Entrepôt ZI Lyon Sud", "69 Lyon – France"],
        "DEVIS N° CDR-2026-1187",
        ["Date : 12/10/2026", "Votre référence : consultation PLV-ECLAT-2026",
         "Interlocutrice : Claire Fontaine, chargée d'affaires"],
        ["Désignation", "Qté", "PU HT (€)", "Total HT (€)"],
        [["Présentoir de sol carton ondulé double cannelure, 4 tablettes + fronton, impression offset "
          "quadri 1 face + vernis acrylique, livré à plat. Dim. 40 × 30 × 165 cm", "2 000", "18,90", "37 800,00"],
         ["Forme de découpe et clichés d'impression", "1", "inclus", "0,00"],
         ["Livraison DAP entrepôt Lyon (20 palettes 80 × 120)", "1", "inclus", "0,00"]],
        [["Total HT", "37 800,00 €"], ["TVA 20 %", "7 560,00 €"], ["Total TTC", "45 360,00 €"]],
        ["Conditions",
         "Incoterm : DAP Lyon, entrepôt Orvalis (Incoterms® 2020)",
         "Délai de livraison : 3 semaines après validation du BAT",
         "Conditions de paiement : 45 jours fin de mois à compter de la date de facture",
         "Validité de l'offre : 60 jours – prix fermes et non révisables pendant la validité",
         "Tolérance de quantité : ± 3 %",
         "BAT numérique sous 48 h ; maquette blanche offerte",
         "Carton certifié FSC® Mix sur demande, sans supplément"],
        "Bon pour accord – Cachet et signature du client :",
    )


def devis_pak_display():
    creer_devis(
        "B_Pak-Display_quotation.pdf", colors.HexColor("#B22222"),
        ["PAK-DISPLAY", "Pak-Display Sp. z o.o.", "ul. Przemyslowa 42", "61-001 Poznan – Poland",
         "EU VAT: PL0000000000"],
        ["<b>Orvalis Cosmetiques</b>", "Purchasing Department", "Lyon – France"],
        "QUOTATION No. PD/Q/2026/0954",
        ["Date: 14 October 2026", "Your ref.: PLV-ECLAT-2026", "Valid until: 13 November 2026",
         "Contact: Tomasz Nowicki, Key Account Manager"],
        ["Description", "Qty", "Unit price (EUR)", "Amount (EUR)"],
        [["Floor display stand, corrugated board EB flute, 4 shelves + header, 4-colour offset print, "
          "matt varnish, flat-packed. Size 400 × 300 × 1650 mm", "2 000", "13.40", "26 800.00"],
         ["Cutting die & printing plates (one-off cost)", "1", "1 450.00", "1 450.00"],
         ["Packing on EUR pallets", "20", "9.00", "180.00"]],
        [["Total net", "EUR 28 430.00"], ["VAT 0 % – intra-EU reverse charge", "EUR 0.00"],
         ["Total", "EUR 28 430.00"]],
        ["Terms and conditions",
         "Delivery terms: FCA Poznan (Incoterms® 2020)",
         "Lead time: 4 weeks from artwork approval",
         "Payment terms: 30 days net from invoice date",
         "Volume discount: 3 % for quantities of 2 500 pcs and above",
         "Price adjustment clause: prices are based on the corrugated board index of September 2026. "
         "Should the index vary by more than 5 % before order confirmation, prices may be adjusted accordingly.",
         "Over/under delivery of ± 5 % invoiced at unit price",
         "Samples: 2 white samples free of charge; printed prototype EUR 250.00"],
        "Best regards, Tomasz Nowicki",
    )


def proforma_anatolia():
    creer_devis(
        "D_Anatolia_Ambalaj_proforma.pdf", colors.HexColor("#2E7D32"),
        ["ANATOLIA AMBALAJ", "Anatolia Ambalaj San. ve Tic. A.S.", "Organize Sanayi Bolgesi, 3. Cadde No. 18",
         "34000 Istanbul – Turkey", "export@anatolia-ambalaj.example"],
        ["<b>Orvalis Cosmetiques</b>", "Purchasing Department", "Lyon – France"],
        "PROFORMA INVOICE No. AA-PI-26-3318",
        ["Date: 15.10.2026", "Your ref.: PLV-ECLAT-2026", "Validity: 45 days", "Currency: USD"],
        ["Description", "Qty", "Unit price (USD)", "Amount (USD)"],
        [["Corrugated floor display, 4 shelves + header, CMYK print, 400 × 300 × 1650 mm, flat packed",
          "2 000", "9.20", "18 400.00"],
         ["Cutting die (one-off)", "1", "900.00", "900.00"]],
        [["Total", "USD 19 300.00"]],
        ["Commercial terms",
         "Incoterms: EXW Istanbul factory (Incoterms® 2020)",
         "Payment: 30 % advance by T/T with order, 70 % balance by T/T before shipment",
         "Production lead time: 7 weeks after receipt of advance payment and artwork approval",
         "Packing: export pallets, approx. 20 pallets",
         "Country of origin: Turkey – A.TR movement certificate available on request",
         "Quality: AQL 2.5 final inspection by our QC department"],
        "Authorised signature – Anatolia Ambalaj export department",
    )


def generer_apercus():
    """Crée une image PNG de chaque PDF (affichée dans l'application). Utilise l'outil « sips » de macOS."""
    apercus = DOSSIER / "apercus"
    apercus.mkdir(exist_ok=True)
    for pdf in DOSSIER.glob("*.pdf"):
        subprocess.run(["sips", "-s", "format", "png", "-Z", "1400", str(pdf), "--out",
                        str(apercus / f"{pdf.stem}.png")], check=True, capture_output=True)


if __name__ == "__main__":
    DOSSIER.mkdir(parents=True, exist_ok=True)
    devis_cartonnages_du_rhone()
    devis_pak_display()
    proforma_anatolia()
    generer_apercus()
    print("Devis et aperçus générés dans", DOSSIER)
