"""Calcule des trajets tests dans le Tarn et mesure les routes interdites empruntées.

Pour chaque paire de lieux tirée au hasard, compare :
- « GPS classique » : profil voiture (auto) de Valhalla ;
- « VSP » : profil motor_scooter limité à 45 km/h,
sur le graphe brut (OSM tel quel) et sur le graphe corrigé.

Produit `sortie/resultats.json` et `sortie/rapport.md`.
Usage : python3 tester.py [nombre_de_paires]
"""

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import valhalla

GRAINE = 81
SEUIL_KM = 0.05  # en dessous, on considère un artefact d'accroche
INTERDITES = ("autoroute", "route_express", "interdite_tag")
PROFILS = {
    "gps_classique": ("auto", {}),
    "vsp": ("motor_scooter", {"motor_scooter": {"top_speed": 45}}),
}


def distance_km(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp, dl = p2 - p1, math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def tirer_paires(lieux, n):
    alea = random.Random(GRAINE)
    paires = []
    while len(paires) < n:
        a, b = alea.sample(lieux, 2)
        if 5 <= distance_km(a, b) <= 60:
            paires.append((a, b))
    return paires


def itineraire(acteur, a, b, costing, options):
    requete = {
        "locations": [{"lat": a["lat"], "lon": a["lon"]}, {"lat": b["lat"], "lon": b["lon"]}],
        "costing": costing, "costing_options": options, "units": "kilometers",
    }
    trajet = acteur.route(requete)["trip"]
    forme = trajet["legs"][0]["shape"]
    attributs = acteur.trace_attributes({
        "encoded_polyline": forme, "shape_match": "edge_walk",
        "costing": costing, "costing_options": options,
        "filters": {"attributes": ["edge.way_id", "edge.length"], "action": "include"},
    })
    return trajet["summary"], [(e["way_id"], e["length"]) for e in attributs["edges"]]


def main(n):
    inventaire = json.loads(Path("sortie/inventaire.json").read_text())
    classes = {v["id"]: v for v in inventaire["voies"]}
    paires = tirer_paires(inventaire["lieux"], n)

    resultats = {}
    for variante in ("brut", "corrige"):
        acteur = valhalla.Actor(f"graphes/{variante}/valhalla.json")
        for profil, (costing, options) in PROFILS.items():
            cle = f"{variante}/{profil}"
            trajets, echecs = [], 0
            for a, b in paires:
                try:
                    resume, aretes = itineraire(acteur, a, b, costing, options)
                except RuntimeError:
                    echecs += 1
                    continue
                km_classe = defaultdict(float)
                for way_id, km in aretes:
                    km_classe[classes[way_id]["classe"] if way_id in classes else "autre"] += km
                trajets.append({
                    "de": a["nom"], "a": b["nom"], "km": resume["length"], "minutes": resume["time"] / 60,
                    "km_classe": dict(km_classe),
                    "voies": sorted({w for w, km in aretes if w in classes and classes[w]["classe"] != "nationale"}),
                })
            resultats[cle] = {"trajets": trajets, "echecs": echecs}
            print(cle, len(trajets), "trajets,", echecs, "échecs")

    Path("sortie/resultats.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=1))
    Path("sortie/rapport.md").write_text(rapport(resultats, classes, n))
    print(Path("sortie/rapport.md").read_text())


def part(trajets, test):
    return sum(1 for t in trajets if test(t)) / len(trajets) if trajets else 0


def utilise(t, classe_voie):
    return t["km_classe"].get(classe_voie, 0) > SEUIL_KM


def detours(resultats):
    """Coût du détour VSP sur les trajets où un GPS classique prend une voie interdite."""
    auto = {(t["de"], t["a"]): t for t in resultats["brut/gps_classique"]["trajets"]}
    ecarts = []
    for t in resultats["brut/vsp"]["trajets"]:
        ref = auto.get((t["de"], t["a"]))
        if ref and any(utilise(ref, c) for c in INTERDITES):
            ecarts.append((t["km"] / ref["km"], t["minutes"] / ref["minutes"]))
    if not ecarts:
        return []
    km = sorted(e[0] for e in ecarts)
    mn = sorted(e[1] for e in ecarts)
    return ["## Détours imposés par les interdictions\n",
            f"Sur les {len(ecarts)} trajets où un GPS classique emprunte une voie interdite aux VSP, "
            f"l'itinéraire VSP est en médiane {km[len(km) // 2] - 1:+.0%} plus long en distance "
            f"et {mn[len(mn) // 2] - 1:+.0%} plus long en temps (45 km/h maximum compris).\n"]


def rapport(resultats, classes, n):
    lignes = [f"# Test du routage VSP dans le Tarn\n\n{n} paires de lieux tirées au hasard (graine {GRAINE}), "
              "distance à vol d'oiseau entre 5 et 60 km.\n",
              "| Graphe / profil | Trajets | Autoroute | Route express | Interdite (tag) | Suspecte | Vitesse moyenne |",
              "|---|---|---|---|---|---|---|"]
    for cle, r in resultats.items():
        t = r["trajets"]
        km = sum(x["km"] for x in t)
        h = sum(x["minutes"] for x in t) / 60
        lignes.append(f"| {cle} | {len(t)} | {part(t, lambda x: utilise(x, 'autoroute')):.1%} "
                      f"| {part(t, lambda x: utilise(x, 'route_express')):.1%} "
                      f"| {part(t, lambda x: utilise(x, 'interdite_tag')):.1%} "
                      f"| {part(t, lambda x: utilise(x, 'suspecte')):.1%} | {km / h if h else 0:.1f} km/h |")

    lignes.append("\nUn trajet compte s'il parcourt plus de 50 m sur la catégorie.\n")
    lignes += detours(resultats)
    lignes += ["## Voies interdites ou suspectes empruntées par le profil VSP (graphe brut)\n",
               "| Voie OSM | Réf. / nom | Classe | maxspeed | Trajets |", "|---|---|---|---|---|"]
    compte = Counter(w for t in resultats["brut/vsp"]["trajets"] for w in t["voies"])
    for w, nb in compte.most_common(30):
        v = classes[w]
        nom = v["tags"].get("ref") or v["tags"].get("name") or "?"
        lignes.append(f"| [{w}](https://www.openstreetmap.org/way/{w}) | {nom} | {v['classe']} "
                      f"| {v['tags'].get('maxspeed', '-')} | {nb} |")
    if not compte:
        lignes.append("| aucune | | | | |")
    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
