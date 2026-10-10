# Test du routage VSP dans le Tarn

400 paires de lieux tirées au hasard (graine 81), distance à vol d'oiseau entre 5 et 60 km.

| Graphe / profil | Trajets | Autoroute | Route express | Interdite (tag) | Suspecte | Vitesse moyenne |
|---|---|---|---|---|---|---|
| brut/gps_classique | 400 | 16.5% | 35.8% | 12.5% | 2.8% | 67.1 km/h |
| brut/vsp | 400 | 0.0% | 0.0% | 0.0% | 0.0% | 42.8 km/h |
| corrige/gps_classique | 400 | 16.5% | 35.8% | 12.5% | 2.8% | 67.1 km/h |
| corrige/vsp | 400 | 0.0% | 0.0% | 0.0% | 0.0% | 42.8 km/h |

Un trajet compte s'il parcourt plus de 50 m sur la catégorie.

## Détours imposés par les interdictions

Sur les 175 trajets où un GPS classique emprunte une voie interdite aux VSP, l'itinéraire VSP est en médiane -2% plus long en distance et +60% plus long en temps (45 km/h maximum compris).

## Voies interdites ou suspectes empruntées par le profil VSP (graphe brut)

| Voie OSM | Réf. / nom | Classe | maxspeed | Trajets |
|---|---|---|---|---|
| aucune | | | | |
