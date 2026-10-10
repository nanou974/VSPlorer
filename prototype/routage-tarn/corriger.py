"""Produit un extrait OSM « corrigé VSP » à partir de l'inventaire.

Ajoute moped=no aux voies que l'inventaire classe comme route express
ou suspecte, pour que le profil VSP de Valhalla les évite. C'est la
parade proposée dans l'étude contre les voies express mal renseignées.

Usage : python3 corriger.py donnees/tarn.osm.pbf donnees/tarn-corrige.osm.pbf
"""

import json
import sys
from pathlib import Path

import osmium

A_FERMER = {"route_express", "suspecte"}


def main(source, cible):
    inventaire = json.loads(Path("sortie/inventaire.json").read_text())
    ids = {v["id"] for v in inventaire["voies"] if v["classe"] in A_FERMER}

    Path(cible).unlink(missing_ok=True)
    with osmium.SimpleWriter(cible) as ecrivain:
        for obj in osmium.FileProcessor(source):
            if obj.is_way() and obj.id in ids:
                tags = dict(obj.tags)
                tags["moped"] = "no"
                obj = obj.replace(tags=tags)
            ecrivain.add(obj)
    print(f"{len(ids)} voies fermées aux VSP dans {cible}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
