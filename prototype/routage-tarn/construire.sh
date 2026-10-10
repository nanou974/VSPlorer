#!/usr/bin/env bash
# Construit les graphes Valhalla du Tarn : brut (OSM tel quel) et corrigé.
# Usage : ./construire.sh   (après inventaire.py)
set -euo pipefail
cd "$(dirname "$0")"

python3 corriger.py donnees/tarn.osm.pbf donnees/tarn-corrige.osm.pbf

for variante in brut corrige; do
  pbf=donnees/tarn.osm.pbf
  [ "$variante" = corrige ] && pbf=donnees/tarn-corrige.osm.pbf
  dossier=graphes/$variante
  rm -rf "$dossier" && mkdir -p "$dossier"
  valhalla_build_config --mjolnir-tile-dir "$dossier/tuiles" \
    --mjolnir-tile-extract "$dossier/tuiles.tar" \
    --mjolnir-admin "$dossier/admins.sqlite" \
    --mjolnir-timezone "$dossier/timezones.sqlite" > "$dossier/valhalla.json"
  valhalla_build_admins -c "$dossier/valhalla.json" "$pbf"
  valhalla_build_tiles -c "$dossier/valhalla.json" "$pbf"
  valhalla_build_extract -c "$dossier/valhalla.json" -v
done
