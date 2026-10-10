# Prototype : test du routage VSP dans le Tarn

Mesure si un calcul d'itinéraire « VSP » fait passer une voiture sans permis par une route
qui lui est interdite (autoroute, route express), à partir des données OpenStreetMap
telles quelles. C'est le risque n°1 identifié dans l'[étude de faisabilité](../../docs/etude-faisabilite.md).

## Méthode

1. **Extrait OSM** du Tarn (rectangle 1,40–3,10 E / 43,30–44,30 N).
2. **Inventaire** (`inventaire.py`) : chaque voie rapide est classée en
   - `autoroute` : `highway=motorway` ;
   - `route_express` : `motorroad=yes` ;
   - `interdite_tag` : `moped=no` ou `motor_vehicle=no` ;
   - `suspecte` : `trunk` à chaussées séparées et 90 km/h ou plus sans `motorroad=yes`,
     ou portant un numéro d'autoroute (« A … ») sans être classée autoroute.
3. **Correction** (`corriger.py`) : ajoute `moped=no` aux voies express et suspectes.
4. **Graphes** (`construire.sh`) : Valhalla construit un graphe brut et un graphe corrigé.
5. **Trajets tests** (`tester.py`) : 400 paires de villes et villages du Tarn tirées au hasard
   (5 à 60 km à vol d'oiseau), calculées avec le profil voiture (« GPS classique ») et le
   profil `motor_scooter` limité à 45 km/h (« VSP »). Chaque trajet est décomposé voie par voie.

## Reproduire

```bash
pip install pyvalhalla osmium shapely
# osmium-tool (apt) pour l'extraction
mkdir -p donnees
curl -L https://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf \
  | osmium extract -b 1.40,43.30,3.10,44.30 -s simple -F pbf - -o donnees/tarn.osm.pbf
python3 inventaire.py donnees/tarn.osm.pbf
./construire.sh
python3 tester.py 400
```

Résultats : [`sortie/rapport.md`](sortie/rapport.md) et `sortie/resultats.json`.

Données © contributeurs OpenStreetMap, licence ODbL.
