import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib.donnees import extractions_corrigees, hypotheses_courantes, montant, ponderation_courante, scenario_actif
from lib.style import DRAPEAUX, bandeau, e
from lib.tco import COURTS, CRITERES, FAMILLES, POSTES, analyser

# Palette catégorielle validée (ordre fixe) : une couleur par famille de coûts / par critère.
COULEURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

scenario = scenario_actif()
besoin = scenario["besoin"]
fournisseurs = scenario["fournisseurs"]
devis = extractions_corrigees(scenario)
hyp = hypotheses_courantes(scenario)


def nom_court(d):
    return f"{DRAPEAUX.get(d['pays'], '')} {fournisseurs[d['id']]['nom']}"


def virgule(texte):
    return texte.replace(".", ",")


bandeau("Étape 2 sur 3 · Coût complet et décision", "Le moins cher sur le devis l'est-il vraiment ?",
        f"Combien coûte <b>réellement</b> chaque offre pour {besoin['quantite']:,} {e(besoin['unite'])}, "
        "transport, douane, outillage, trésorerie, change, non-qualité et excédent compris ? "
        "Puis quelle offre retenir selon <b>vos</b> priorités ?".replace(",", " ", 1))

# --- Hypothèses modifiables -----------------------------------------------------------------------------------
with st.expander("Hypothèses de l'acheteur (modifiables)", icon=":material/tune:"):
    hg = hyp["generales"]
    c1, c2, c3, c4 = st.columns(4)
    hg["taux_change"]["USD"] = c1.number_input("1 € = … USD", value=float(hg["taux_change"]["USD"]), step=0.01,
                                                format="%.2f", key="hyp_usd")
    hg["provision_risque_change"] = c1.number_input(
        "Provision risque de change (%)", value=hg["provision_risque_change"] * 100, step=0.5, format="%g",
        key="hyp_change") / 100
    hg["taux_financement_annuel"] = c2.number_input(
        "Coût de l'argent (% par an)", value=hg["taux_financement_annuel"] * 100, step=0.5, format="%g",
        key="hyp_fin") / 100
    hg["cout_par_defaut_qualite_eur"] = c2.number_input(
        "Coût d'un présentoir défectueux (€)", value=float(hg["cout_par_defaut_qualite_eur"]), step=5.0,
        format="%g", key="hyp_defaut", help="Tri, retour, remplacement en urgence")
    hg["valeur_residuelle_excedent"] = c3.number_input(
        "Valeur récupérée sur l'excédent (%)", value=hg["valeur_residuelle_excedent"] * 100, step=5.0,
        format="%g", key="hyp_resid") / 100
    hg["cout_stockage_palette_mois_eur"] = c3.number_input(
        "Stockage (€ / palette / mois)", value=float(hg["cout_stockage_palette_mois_eur"]), step=1.0,
        format="%g", key="hyp_stock")
    hg["date_commande"] = c4.date_input("Date de commande prévue", value=pd.Timestamp(hg["date_commande"]),
                                         format="DD/MM/YYYY", key="hyp_date").isoformat()
    hg["bat_jours"] = c4.number_input("Délai de validation du BAT (jours)", value=int(hg["bat_jours"]), step=1,
                                      key="hyp_bat")

    st.markdown("**Par fournisseur**")
    colonnes = {"transport_eur": "Transport (€)", "taux_assurance_transport": "Assurance (taux)",
                "dedouanement_export_eur": "Dédouan. export (€)", "dedouanement_import_eur": "Dédouan. import (€)",
                "taux_droits_douane": "Droits de douane (taux)", "cout_qualification_eur": "Qualification (€)",
                "taux_defaut_estime": "Taux de défaut", "transit_jours": "Transit (jours)"}
    tableau = pd.DataFrame({fournisseurs[i]["nom"]: {k: v[k] for k in colonnes}
                            for i, v in hyp["par_fournisseur"].items()}).T
    modifie = st.data_editor(tableau, key="hyp_fournisseurs", width="stretch",
                             column_config={k: st.column_config.NumberColumn(v, format="%g")
                                            for k, v in colonnes.items()})
    for i, v in hyp["par_fournisseur"].items():
        v.update({k: float(modifie.loc[fournisseurs[i]["nom"], k]) for k in colonnes})
    st.caption("Douane : le papier et le carton (chapitre 48) entrent dans l'UE à 0 % de droits ; "
               "la TVA à l'import est récupérable, ce n'est donc pas un coût.")

# --- Calculs ----------------------------------------------------------------------------------------------------
# Les curseurs sont affichés plus bas, mais leur valeur sert déjà aux cartes du haut.
poids, exclure_retards = ponderation_courante()
analyse = analyser(devis, besoin, fournisseurs, hyp, poids, exclure_retards)
resultats, notes, scores = analyse["resultats"], analyse["notes"], analyse["scores"]
classement, gagnant = analyse["classement"], analyse["gagnant"]
moins_cher_devis, moins_cher_tco = analyse["moins_cher_devis"], analyse["moins_cher_tco"]

# --- Prix affiché contre coût complet ---------------------------------------------------------------------------
st.markdown("#### Prix affiché ou coût réel ?")
cartes = []
for d in devis:
    r = resultats[d["id"]]
    ecart = (r["unitaire"] - r["prix_affiche_eur"]) / r["prix_affiche_eur"]
    etiquettes = []
    if d["id"] == gagnant:
        etiquettes.append(("verte", "★ Recommandé"))
    if d["id"] == moins_cher_tco:
        etiquettes.append(("verte", "Le moins cher en coût complet"))
    if d["id"] == moins_cher_devis:
        etiquettes.append(("grise", "Le moins cher sur le devis"))
    if r["marge_jours"] < 0:
        etiquettes.append(("rouge", f"Livré {-r['marge_jours']} j trop tard"))
    cartes.append(
        f'<div class="carte-f{" gagnant" if d["id"] == gagnant else ""}">'
        f'<div class="entete">{e(nom_court(d))}</div>'
        f'<div class="pays">{e(d["pays"])} · {e(fournisseurs[d["id"]]["statut"])}</div>'
        f'<div class="lib">Coût complet par présentoir</div>'
        f'<div class="tco">{montant(r["unitaire"])}</div>'
        f'<div class="affiche">Prix affiché {montant(r["prix_affiche_eur"])} '
        f'<span class="ecart {"hausse" if ecart > 0 else "baisse"}">{virgule(f"{ecart:+.0%}")}</span></div>'
        f'<div class="ligne"><span>Devis HT</span><b>{montant(r["montant_devis"], decimales=0)}</b></div>'
        f'<div class="ligne"><span>Coût complet</span><b>{montant(r["total"], decimales=0)}</b></div>'
        f'<div class="ligne"><span>Livraison</span><b>{r["livraison"]:%d/%m/%Y}</b></div>'
        + "".join(f'<span class="etiquette {c}">{e(t)}</span>' for c, t in etiquettes) + "</div>")
st.html(f'<div class="chiffres" style="grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));">'
        f'{"".join(cartes)}</div>')

# Graphique : coût par présentoir, empilé par famille de coûts
fig = go.Figure()
for famille, couleur in zip(FAMILLES, COULEURS):
    valeurs = [sum(v for p, v in resultats[d["id"]]["postes"].items() if POSTES[p] == famille) / besoin["quantite"]
               for d in devis]
    fig.add_bar(name=famille, y=[nom_court(d) for d in devis], x=valeurs, orientation="h",
                marker=dict(color=couleur, line=dict(color="white", width=2)),
                hovertemplate="%{y}<br>" + famille + " : %{x:.2f} € / présentoir<extra></extra>")
fig.add_scatter(name="Prix affiché", y=[nom_court(d) for d in devis],
                x=[resultats[d["id"]]["prix_affiche_eur"] for d in devis], mode="markers",
                marker=dict(symbol="line-ns", size=26, line=dict(width=3, color="#16243A")),
                hovertemplate="%{y}<br>Prix affiché : %{x:.2f} €<extra></extra>")
for d in devis:
    fig.add_annotation(x=resultats[d["id"]]["unitaire"], y=nom_court(d),
                       text=f"<b>{montant(resultats[d['id']]['unitaire'])}</b>",
                       showarrow=False, xanchor="left", xshift=8, font=dict(color="#16243A"))
fig.update_layout(barmode="relative", height=340, margin=dict(l=10, r=80, t=40, b=10),
                  title=dict(text="Coût complet par présentoir (€), par famille de coûts", font=dict(size=15)),
                  legend=dict(orientation="h", y=-0.15), plot_bgcolor="white", paper_bgcolor="white",
                  font=dict(family="Inter, sans-serif", color="#16243A"),
                  xaxis=dict(gridcolor="#E6E9EE", zerolinecolor="#9AA3AF", ticksuffix=" €"),
                  yaxis=dict(autorange="reversed"))
with st.container(border=True):
    st.plotly_chart(fig, width="stretch")
    with st.expander("Détail du calcul, poste par poste", icon=":material/table:"):
        detail = pd.DataFrame({nom_court(d): resultats[d["id"]]["postes"] for d in devis})
        detail.loc["TOTAL coût complet"] = detail.sum()
        detail.loc["Coût complet par présentoir"] = [resultats[d["id"]]["unitaire"] for d in devis]
        st.dataframe(detail.map(lambda v: montant(v, decimales=0) if abs(v) >= 100 or v == 0 else montant(v)),
                     width="stretch")
        st.caption("Trésorerie : référence = paiement le jour de la livraison. Payer après la livraison est un "
                   "gain, payer avant (acompte) est un coût. Excédent : unités imposées par le minimum de commande, "
                   "diminuées de leur valeur récupérable, plus leur stockage.")

# --- Matrice de décision ----------------------------------------------------------------------------------------
st.markdown("#### Matrice de décision pondérée")
with st.container(border=True):
    st.markdown("**Réglez l'importance de chaque critère** : le classement et la recommandation se mettent à jour.")
    for col, (cle, libelle) in zip(st.columns(len(CRITERES)), CRITERES.items()):
        col.slider(libelle, 0, 100, poids[cle], step=5, format="%d %%", key=f"poids_{cle}")
    total_poids = sum(poids.values())
    if total_poids != 100:
        st.caption(f"Total des poids : {total_poids} %. Les poids sont ramenés automatiquement à 100 %.")
    st.toggle("Éliminer les offres livrées après la date de besoin "
              f"({pd.Timestamp(besoin['date_besoin']):%d/%m/%Y})", value=exclure_retards, key="exclure_retards")

    ordre = classement + [i for i in scores if scores[i] is None]
    par_id = {d["id"]: d for d in devis}
    matrice = pd.DataFrame([{
        "Rang": str(classement.index(i) + 1) if i in classement else "Éliminé",
        "Fournisseur": nom_court(par_id[i]),
        **{COURTS[c]: notes[i][c] for c in CRITERES},
        "Score pondéré": scores[i],
    } for i in ordre])
    st.dataframe(
        matrice, hide_index=True, width="stretch",
        column_config={**{COURTS[c]: st.column_config.ProgressColumn(COURTS[c], min_value=0, max_value=10,
                                                                     format="%.1f", help=CRITERES[c])
                          for c in CRITERES},
                       "Score pondéré": st.column_config.NumberColumn("Score / 10", format="%.2f")},
    )

    fig2 = go.Figure()
    for (cle, libelle), couleur in zip(CRITERES.items(), COULEURS):
        fig2.add_bar(name=libelle, y=[nom_court(par_id[i]) for i in classement], orientation="h",
                     x=[notes[i][cle] * poids[cle] / (total_poids or 1) for i in classement],
                     marker=dict(color=couleur, line=dict(color="white", width=2)),
                     hovertemplate="%{y}<br>" + libelle + " : %{x:.2f} point(s)<extra></extra>")
    fig2.update_layout(barmode="stack", height=90 + 55 * len(classement), margin=dict(l=10, r=10, t=40, b=10),
                       title=dict(text="Ce qui fait le score de chaque fournisseur (sur 10)", font=dict(size=15)),
                       legend=dict(orientation="h", y=-0.25, traceorder="normal"), plot_bgcolor="white",
                       paper_bgcolor="white",
                       font=dict(family="Inter, sans-serif", color="#16243A"),
                       xaxis=dict(range=[0, 10], gridcolor="#E6E9EE"), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, width="stretch")

    with st.expander("Comment les notes sont-elles calculées ?", icon=":material/help:"):
        st.markdown(
            "- **Coût complet** : 10 pour l'offre la moins chère, les autres en proportion (TCO min ÷ TCO).\n"
            "- **Délai** : 0 si la livraison arrive après la date de besoin ; de 5 à 10 selon la marge de sécurité "
            "(10 à partir de 3 semaines d'avance).\n"
            "- **Qualité** : 10 moins 2 points par % de défauts attendus ; −1 sans certification ISO 9001.\n"
            "- **Risque fournisseur** : 70 % santé financière (note de solvabilité) et 30 % autres risques "
            "(incidents de paiement −4, fournisseur hors UE −3).\n"
            "- **Conditions de paiement** : selon la date moyenne de paiement, acompte compris "
            "(0 si l'on paie 30 jours avant la livraison, 10 à 60 jours après, plafond légal en France)."
        )

# --- Recommandation -------------------------------------------------------------------------------------------
if len(classement) >= 2:
    premier, second = par_id[classement[0]], par_id[classement[1]]
    # Points forts : critères où le premier prend le plus de points d'avance sur le second.
    avance = {c: (notes[premier["id"]][c] - notes[second["id"]][c]) * poids[c] for c in CRITERES}
    forces = [COURTS[c].lower() for c in sorted(avance, key=avance.get, reverse=True)[:2] if avance[c] > 0]
    paragraphes = [f"Il devance <b>{e(nom_court(second))}</b> ({virgule(f'{scores[second['id']]:.2f}')}/10)"
                   + (f", grâce à son avantage sur : {e(' et '.join(forces))}." if forces else ".")]
    ecart_tco = resultats[premier["id"]]["total"] - resultats[moins_cher_tco]["total"]
    if premier["id"] != moins_cher_tco:
        paragraphes.append(
            f"Ce n'est pas l'offre la moins chère : <b>{montant(ecart_tco, decimales=0)} de plus</b> que "
            f"{e(nom_court(par_id[moins_cher_tco]))} en coût complet. C'est le prix de la sécurité, et c'est "
            "<b>la base de la négociation</b> (étape 3).")
    retards = [nom_court(d) for d in devis if resultats[d["id"]]["marge_jours"] < 0]
    if retards:
        paragraphes.append(f"⚠ {e(', '.join(retards))} livrerait après la date de besoin.")
    st.html(f'<div class="reco"><div class="titre">Recommandation de l\'acheteur</div>'
            f'<div class="gagnant">★ {e(nom_court(premier))} · {virgule(f"{scores[premier["id"]]:.2f}")}/10</div>'
            + "".join(f"<p>{p}</p>" for p in paragraphes) + "</div>")
    st.page_link("vues/negociation.py", label="Préparer la négociation (étape 3)", icon=":material/arrow_forward:")
