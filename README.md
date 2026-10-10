# VSPlorer

GPS gratuit et open source pour voitures sans permis : itinéraires sans autoroutes ni voies rapides, consommation estimée selon votre modèle, stations et bornes sur le trajet.

> Projet au stade de la conception : aucune application n'est encore disponible.

## Objectifs

- **Itinéraires adaptés aux VSP** (quadricycles légers L6e, 45 km/h) : jamais d'autoroute ni de route express.
- **Temps de trajet réaliste**, calculé à 45 km/h maximum.
- **Consommation estimée** selon la marque, le modèle et la motorisation, affinée avec les pleins ou recharges saisis.
- **Stations-service et bornes de recharge** compatibles, autour de soi ou sur le trajet.
- **Fonctionne hors ligne**, sans compte, sans publicité, sans pistage.
- **100 % gratuit.**

## Vie privée

- La position reste sur le téléphone.
- La carte grise peut être lue par la caméra pour identifier le véhicule, mais elle **n'est jamais enregistrée** : seuls les champs techniques (marque, modèle, type, cylindrée, puissance, masse) sont conservés ; nom, adresse, plaque et numéro de série sont ignorés.

## Pile technique prévue

| Brique | Choix |
|---|---|
| Données cartographiques | OpenStreetMap |
| Calcul d'itinéraire (sur le téléphone) | Valhalla, profil VSP à 45 km/h |
| Guidage et carte | Ferrostar + MapLibre Native |
| Recherche d'adresse | API Adresse / Géoplateforme (IGN) |
| Stations et bornes | Prix des carburants + base nationale IRVE (data.gouv.fr) |

Android d'abord, iOS ensuite.

## Contenu du dépôt

- [`docs/etude-faisabilite.md`](docs/etude-faisabilite.md) : étude de faisabilité, risques et feuille de route.
- [`data/base-vehicules-vsp.xlsx`](data/base-vehicules-vsp.xlsx) : base des véhicules (une ligne par motorisation, avec sa source).
- [`data/vehicules.csv`](data/vehicules.csv) : export CSV de cette base, pour l'application.

## Données

Cartes © contributeurs [OpenStreetMap](https://www.openstreetmap.org/copyright), sous licence ODbL.
