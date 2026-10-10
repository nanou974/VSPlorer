"""Inventaire OSM du Tarn : routes rapides et points de départ/arrivée.

Lit l'extrait OSM, reconstruit le contour du département (relation admin
niveau 6, ref 81) et produit `sortie/inventaire.json` :
- les voies motorway / trunk avec leurs tags et leur classement VSP ;
- les lieux habités (ville, bourg, village) situés dans le Tarn.

Usage : python3 inventaire.py donnees/tarn.osm.pbf
"""

import json
import math
import sys
from pathlib import Path

import osmium
from shapely import wkb
from shapely.geometry import Point

RAPIDES = {"motorway", "motorway_link", "trunk", "trunk_link"}
LIEUX = {"city", "town", "village"}


def vitesse(tags):
    """maxspeed en km/h, ou None si absent ou non numérique."""
    try:
        return int(str(tags.get("maxspeed", "")).split()[0])
    except (ValueError, IndexError):
        return None


def classer(tags):
    """Classe une voie rapide du point de vue d'une VSP.

    - autoroute : interdite (Code de la route, art. R421-2)
    - route_express : interdite, signalée par motorroad=yes
    - interdite_tag : interdite explicitement aux cyclomoteurs (moped=no)
    - suspecte : route à chaussées séparées, 90 km/h ou plus, sans
      motorroad=yes, ou portant un numéro d'autoroute. Souvent une voie
      express mal renseignée dans OSM.
    - nationale : autre route classée trunk, a priori autorisée
    """
    hw = tags.get("highway")
    if hw in ("motorway", "motorway_link"):
        return "autoroute"
    if tags.get("motorroad") == "yes":
        return "route_express"
    if tags.get("moped") == "no" or tags.get("motor_vehicle") == "no":
        return "interdite_tag"
    if hw not in RAPIDES:
        return "autre"
    v = vitesse(tags)
    separee = tags.get("oneway") == "yes" or tags.get("expressway") == "yes"
    if hw == "trunk" and separee and (v is None or v >= 90):
        return "suspecte"
    if str(tags.get("ref", "")).startswith("A "):
        return "suspecte"  # numéro d'autoroute sur une voie non classée autoroute
    return "nationale"


def longueur_km(coords):
    total = 0.0
    for (lon1, lat1), (lon2, lat2) in zip(coords, coords[1:]):
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = p2 - p1, math.radians(lon2 - lon1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        total += 2 * 6371.0 * math.asin(math.sqrt(a))
    return total


def main(pbf):
    fabrique = osmium.geom.WKBFactory()
    tarn = None
    voies, lieux = [], []

    for obj in osmium.FileProcessor(pbf).with_locations().with_areas():
        tags = dict(obj.tags)
        if obj.is_area():
            if (tags.get("boundary") == "administrative" and tags.get("admin_level") == "6"
                    and tags.get("ref") == "81"):
                tarn = wkb.loads(fabrique.create_multipolygon(obj), hex=True)
        elif obj.is_way() and "highway" in tags and (
                tags["highway"] in RAPIDES or tags.get("motorroad") == "yes"
                or tags.get("moped") == "no" or tags.get("motor_vehicle") == "no"):
            coords = [(n.lon, n.lat) for n in obj.nodes if n.location.valid()]
            if len(coords) < 2:
                continue
            voies.append({
                "id": obj.id,
                "highway": tags["highway"],
                "classe": classer(tags),
                "km": round(longueur_km(coords), 3),
                "milieu": coords[len(coords) // 2],
                "tags": {k: tags[k] for k in ("ref", "name", "maxspeed", "oneway", "motorroad",
                                              "expressway", "moped", "motor_vehicle") if k in tags},
            })
        elif obj.is_node() and tags.get("place") in LIEUX:
            lieux.append({"id": obj.id, "nom": tags.get("name", "?"), "type": tags["place"],
                          "lon": obj.location.lon, "lat": obj.location.lat})

    if tarn is None:
        sys.exit("Contour du Tarn introuvable dans l'extrait.")

    for v in voies:
        v["dans_tarn"] = tarn.contains(Point(v["milieu"]))
    lieux = [l for l in lieux if tarn.contains(Point(l["lon"], l["lat"]))]

    sortie = Path("sortie")
    sortie.mkdir(exist_ok=True)
    (sortie / "inventaire.json").write_text(json.dumps(
        {"voies": voies, "lieux": lieux, "contour_tarn": tarn.wkt}, ensure_ascii=False))

    bilan = {}
    for v in voies:
        if v["dans_tarn"]:
            bilan[v["classe"]] = bilan.get(v["classe"], 0) + v["km"]
    print(f"{len(lieux)} lieux habités dans le Tarn")
    for classe, km in sorted(bilan.items()):
        print(f"{classe:15} {km:8.1f} km")


if __name__ == "__main__":
    main(sys.argv[1])
