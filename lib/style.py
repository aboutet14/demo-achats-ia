"""Éléments visuels communs : styles, bandeau d'en-tête, cartes."""
import html

import streamlit as st

DRAPEAUX = {"France": "🇫🇷", "Pologne": "🇵🇱", "Portugal": "🇵🇹", "Turquie": "🇹🇷", "Espagne": "🇪🇸",
            "Italie": "🇮🇹", "Allemagne": "🇩🇪", "Chine": "🇨🇳", "Maroc": "🇲🇦"}

CSS = """
<style>
.block-container {max-width: 1280px; padding-top: 2.2rem;}
[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlock"][style*="border"] {
  background: #FFFFFF; box-shadow: 0 1px 2px rgba(16,36,58,.04), 0 4px 14px rgba(16,36,58,.05);
}
[data-testid="stMetric"] {background: #FFFFFF;}
.stTabs [data-baseweb="tab"] {font-weight: 600;}

.bandeau {background: linear-gradient(120deg, #0F2A47 0%, #1F5A96 70%, #2a78d6 100%); color: #fff;
  border-radius: 16px; padding: 28px 32px; margin-bottom: 18px; position: relative; overflow: hidden;}
.bandeau::after {content: ""; position: absolute; right: -60px; top: -60px; width: 240px; height: 240px;
  border-radius: 50%; background: rgba(255,255,255,.07);}
.bandeau .puce {display: inline-block; background: #F2B544; color: #0F2A47; font-weight: 700; font-size: .75rem;
  letter-spacing: .04em; text-transform: uppercase; padding: 3px 10px; border-radius: 999px; margin-bottom: 10px;}
.bandeau h1 {color: #fff; font-size: 2rem; font-weight: 800; margin: 0 0 6px 0; padding: 0; line-height: 1.2;}
.bandeau p {color: #DCE7F3; font-size: 1.02rem; margin: 0; max-width: 900px;}

.chiffres {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin: 6px 0 22px;}
.chiffre {background: #fff; border: 1px solid #DCE3EC; border-radius: 14px; padding: 16px 18px;}
.chiffre .valeur {font-size: 1.75rem; font-weight: 800; color: #0F2A47; line-height: 1.15;}
.chiffre .libelle {font-size: .86rem; color: #5B6B80; margin-top: 4px;}

.carte-f {background: #fff; border: 1px solid #DCE3EC; border-radius: 14px; padding: 16px 18px; height: 100%;}
.carte-f.gagnant {border: 2px solid #1F8A5B; box-shadow: 0 6px 18px rgba(31,138,91,.12);}
.carte-f .entete {font-weight: 700; font-size: 1rem; color: #16243A; margin-bottom: 2px;}
.carte-f .pays {font-size: .8rem; color: #5B6B80; margin-bottom: 12px;}
.carte-f .lib {font-size: .78rem; color: #5B6B80; text-transform: uppercase; letter-spacing: .04em;}
.carte-f .tco {font-size: 1.9rem; font-weight: 800; color: #0F2A47; line-height: 1.1;}
.carte-f .affiche {font-size: .9rem; color: #5B6B80; margin: 2px 0 10px;}
.carte-f .affiche s {color: #8A97A8;}
.ecart {display: inline-block; font-weight: 700; font-size: .8rem; padding: 2px 8px; border-radius: 999px;}
.ecart.hausse {background: #FBEAEA; color: #A8322D;}
.ecart.baisse {background: #E6F4EC; color: #17724A;}
.carte-f .ligne b {white-space: nowrap;}
.carte-f .ligne {display: flex; justify-content: space-between; gap: 10px; font-size: .85rem; color: #3D4D63;
  border-top: 1px dashed #E3E8EF; padding-top: 6px; margin-top: 6px;}
.etiquette {display: inline-block; font-size: .72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;
  margin: 8px 4px 0 0;}
.etiquette.verte {background: #E6F4EC; color: #17724A;}
.etiquette.grise {background: #EEF2F6; color: #4A5A70;}
.etiquette.rouge {background: #FBEAEA; color: #A8322D;}

.alertes {list-style: none; padding: 0; margin: 4px 0 0;}
.alertes li {background: #FFF8EC; border-left: 4px solid #E3A12F; border-radius: 8px; padding: 9px 12px;
  margin-bottom: 7px; font-size: .9rem; color: #4A3A1A;}
.alertes li.ok {background: #EEF7F2; border-left-color: #1F8A5B; color: #1D4E37;}

.ecart.neutre {background: #EEF2F6; color: #4A5A70;}
.levier {background: #fff; border: 1px solid #DCE3EC; border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;}
.levier .haut {display: flex; justify-content: space-between; align-items: center; gap: 10px; color: #16243A;}
.levier .haut .ecart {white-space: nowrap;}
.levier .arg {font-size: .88rem; color: #4A5A70; margin-top: 4px; line-height: 1.45;}

.levier details {margin-top: 8px; border-top: 1px dashed #E3E8EF; padding-top: 6px;}
.levier summary {cursor: pointer; font-weight: 600; font-size: .86rem; color: #1F5A96;}
.levier details p {font-size: .87rem; color: #2B3A50; line-height: 1.5; margin: 8px 0 0;}
.levier blockquote {margin: 8px 0 0; padding: 8px 12px; background: #F3F7FC; border-left: 3px solid #1F5A96;
  border-radius: 6px; font-size: .88rem; color: #16243A; font-style: italic;}
.technique {display: inline-block; margin-top: 8px; font-size: .74rem; font-weight: 700; color: #7A4F06;
  background: #FFF3DA; padding: 2px 8px; border-radius: 999px;}
.deroule {background: #0F2A47; color: #DCE7F3; border-radius: 14px; padding: 14px 18px; margin-bottom: 14px;}
.deroule .titre {color: #F2B544; font-weight: 800; font-size: .8rem; text-transform: uppercase;
  letter-spacing: .05em;}
.deroule ol {margin: 8px 0 0; padding-left: 20px; font-size: .9rem; line-height: 1.5;}
.deroule li {margin-bottom: 4px;}

.reco {background: #fff; border: 1px solid #DCE3EC; border-left: 6px solid #1F8A5B; border-radius: 14px;
  padding: 18px 22px; margin-top: 8px;}
.reco .titre {font-weight: 800; color: #17724A; text-transform: uppercase; font-size: .8rem; letter-spacing: .05em;}
.reco .gagnant {font-size: 1.35rem; font-weight: 800; color: #0F2A47; margin: 4px 0 8px;}
.reco p {margin: 0 0 6px; color: #2B3A50;}

.etape {background: #fff; border: 1px solid #DCE3EC; border-radius: 14px; padding: 18px; height: 100%;}
.etape .num {display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px;
  border-radius: 50%; background: #0F2A47; color: #F2B544; font-weight: 800; margin-bottom: 10px;}
.etape .num.inactif {background: #EEF2F6; color: #8A97A8;}
.etape .titre {font-weight: 700; font-size: 1.05rem; color: #16243A; margin-bottom: 6px;}
.etape .texte {font-size: .9rem; color: #5B6B80; line-height: 1.45;}

.profil {margin-top: 4px; font-size: .85rem; color: #B9C8DA;}
.profil b {color: #FFFFFF; font-size: .95rem;}
.profil a {color: #F2B544 !important;}
@media (max-width: 640px) {
  .bandeau {padding: 20px 20px;}
  .bandeau h1 {font-size: 1.45rem;}
  .bandeau p {font-size: .95rem;}
  .chiffre .valeur {font-size: 1.4rem;}
}
</style>
"""


def appliquer_style():
    st.html(CSS)


def e(texte):
    """Échappe un texte avant de l'insérer dans du HTML."""
    return html.escape(str(texte))


def bandeau(puce, titre, texte):
    st.html(f'<div class="bandeau"><span class="puce">{e(puce)}</span><h1>{e(titre)}</h1><p>{texte}</p></div>')


def chiffres_cles(elements):
    """elements : liste de (valeur, libellé)."""
    blocs = "".join(f'<div class="chiffre"><div class="valeur">{e(v)}</div><div class="libelle">{e(l)}</div></div>'
                    for v, l in elements)
    st.html(f'<div class="chiffres">{blocs}</div>')


def liste_alertes(points):
    if not points:
        st.html('<ul class="alertes"><li class="ok">✓ Aucun point bloquant repéré.</li></ul>')
        return
    st.html('<ul class="alertes">' + "".join(f"<li>⚠ {e(p)}</li>" for p in points) + "</ul>")
