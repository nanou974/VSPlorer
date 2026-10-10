# Étude de faisabilité : GPS pour voitures sans permis (VSP)

Date : 10/10/2026. Étude sans code. Les points marqués *(à vérifier)* sont des déductions non confirmées par une source.

## Verdict

**Réalisable, entièrement avec des briques gratuites et open source.** Aucune brique manquante : carte, routage personnalisable, guidage vocal sur mobile et recherche d'adresses existent déjà sous licences libres. Le vrai défi n'est pas technique mais tient à **la qualité des données** (savoir précisément quelles routes sont interdites aux VSP) et à **l'effort de développement** du guidage pas-à-pas sur mobile.

La gratuité totale pour l'utilisateur est tenable. Pour toi, le coût minimum réel est d'environ **99 $/an (compte Apple)** + **25 $ une fois (Google Play)**, et l'hébergement peut rester à 0 € si le calcul d'itinéraire se fait sur le téléphone.

## 1. Règles à respecter pour une VSP

- Une VSP est un quadricycle léger (catégorie L6e), vitesse limitée à **45 km/h** par construction.
- **Autoroutes interdites** (Code de la route, art. R421-2, qui cite explicitement les quadricycles légers à moteur).
- **Routes express / voies rapides interdites** (même régime, panneau « route pour automobiles »).
- Quelques interdictions locales par arrêté (tunnels, ponts, certaines rocades) existent en plus.

## 2. Données cartographiques (gratuites)

| Besoin | Source | Licence / coût |
|---|---|---|
| Réseau routier, limitations, accès | **OpenStreetMap** (extrait France sur Geofabrik) | ODbL, gratuit |
| Autoroutes | `highway=motorway` / `motorway_link` | fiable |
| Routes express | `motorroad=yes` (souvent sur `highway=trunk`) | **couverture incomplète en France** |
| Interdictions spécifiques | `moped=no`, `motor_vehicle=no`, `access=*` | partielles |
| Relief (pour la consommation) | SRTM / Copernicus DEM, ou IGN RGE ALTI | gratuit |
| Recherche d'adresses | **API Adresse / Géoplateforme (IGN, data.gouv)** | gratuit, licence ouverte |
| Fond de carte | **OpenFreeMap** ou **Protomaps (PMTiles)** auto-hébergé | gratuit |

À éviter en production : les serveurs publics de tuiles OSM et Nominatim, dont les règles d'usage interdisent un trafic d'application.

## 3. Moteurs de routage open source

| Moteur | Licence | Profil VSP | Hors ligne sur mobile | Avis |
|---|---|---|---|---|
| **Valhalla** | MIT | Profil `motor_scooter` déjà prévu pour véhicules lents (vitesse max réglable, évite autoroutes, respecte `moped=no`), coûts modifiables à chaque requête | Oui (tuiles embarquées) | **Recommandé** |
| GraphHopper | Apache 2.0 | « Custom models » très souples | Possible mais peu maintenu sur mobile | Bon choix côté serveur |
| BRouter | MIT | Profils scriptables | Oui, Android seulement | Pensé vélo, pas d'iOS |
| OSRM | BSD | Profils Lua figés au pré-calcul | Non | Trop rigide |

Pour le guidage pas-à-pas (instructions, recalcul en cas d'écart, voix) : **Ferrostar** (BSD, iOS + Android, compatible Valhalla) + **MapLibre Native** (BSD) pour l'affichage de la carte. Cela évite de réécrire la partie la plus coûteuse d'un GPS.

## 4. Vitesse et consommation

- **Temps de trajet** : vitesse = min(limite de la route, 45 km/h), avec pénalités en côte et en ville. Valhalla le gère nativement (`top_speed`).
- **Consommation** : pas de donnée publique, il faut un **modèle d'estimation** : distance × consommation de base (ordre de grandeur environ 3 L/100 km diesel, environ 6 à 8 kWh/100 km électrique *(à vérifier par modèle)*), majorée selon le dénivelé et les arrêts. Résultat utile mais approximatif, à présenter comme une estimation. Une table par modèle de VSP (Aixam, Ligier, Citroën Ami…) améliorera la précision.
- Option intéressante : choix d'itinéraire « économe » (éviter les fortes pentes), possible avec les coûts de Valhalla (`use_hills`).

### Calcul automatique selon le modèle de VSP (exigence de Gianny, 10/10/2026)

- **Choix du véhicule** au premier lancement, en trois listes enchaînées (exigence de Gianny) :
  1. **Marque** : Ligier, Aixam, Microcar, Chatenet, Citroën, Fiat…
  2. **Modèle** : X-Too, … (filtré par marque)
  3. **Motorisation** : Lombardini, électrique, … (filtrée par modèle)
- **Fiche embarquée par motorisation** : masse, puissance, motorisation (diesel ou électrique), réservoir ou batterie, consommation homologuée, surface frontale estimée.
- **Calcul par tronçon** : résistance au roulement + aérodynamique + pente (relief) + pertes aux arrêts, divisé par le rendement moteur, puis calé sur la consommation homologuée.
- **Électrique** : alerte si le trajet dépasse l'autonomie restante.
- **Correction optionnelle** : saisie des pleins ou recharges pour ajuster le coefficient propre à l'utilisateur.
- **Point à prévoir** : aucune base gratuite de fiches VSP connue, donc à constituer à la main (quelques dizaines de modèles, à partir des fiches constructeurs).
- **Repli carte grise** : si la motorisation est incomplète dans la base, l'app demande cylindrée (P.1), puissance (P.2) et masse à vide (G.1), puis affine avec les pleins saisis.
- **Lecture de la carte grise par photo** (option retenue le 10/10/2026 à la place d'une recherche par plaque) : reconnaissance de texte sur le téléphone (gratuite, hors ligne), champs D.1, D.2, D.3, P.1, P.2, G.1. **Règle RGPD (exigence de Gianny) : la carte grise n'est jamais enregistrée** : lecture du flux caméra en mémoire, aucune photo stockée ni envoyée, seuls les champs techniques conservés (nom, adresse, plaque et VIN ignorés), saisie manuelle possible. La recherche par numéro d'immatriculation est écartée : accès au SIV réservé aux professionnels agréés, services payants à la requête, donnée personnelle (RGPD), et pas de consommation fournie.
- **Précision attendue** : environ ±15–20 % sans calibrage *(estimation à vérifier sur des trajets réels)*.

### Stations et points de recharge (exigence de Gianny, 10/10/2026)

- **Stations-service** : flux « Prix des carburants en France » (prix-carburants.gouv.fr / data.gouv.fr), licence ouverte : position, carburants, horaires, prix, mis à jour en continu.
- **Recharge** : Base nationale des IRVE (data.gouv.fr), licence ouverte. Filtrer selon la motorisation choisie, notamment les bornes avec **prise domestique E/F** (beaucoup de VSP électriques, dont la Citroën Ami, se rechargent sur prise classique).
- **Repli** : points `amenity=fuel` / `amenity=charging_station` d'OSM.
- **Recherche** : autour de la position, ou dans un couloir le long de l'itinéraire, avec le détour affiché.
- **Couplage consommation** : proposer automatiquement un arrêt quand l'autonomie estimée devient insuffisante.
- **Hors ligne** : copie embarquée, actualisée dès qu'il y a du réseau.

## 5. Hors ligne ou serveur ?

| | Routage sur le téléphone | Routage sur serveur |
|---|---|---|
| Coût d'hébergement | ~0 € (fichiers sur Cloudflare R2, sortie gratuite) | 0 € (offre gratuite Oracle Cloud, fragile) à ~10–20 €/mois (VPS) |
| Fonctionne sans réseau | Oui | Non |
| Téléchargement | France : quelques centaines de Mo à ~1–2 Go *(à mesurer)* | Aucun |
| Mise à jour des données | Fichier à republier régulièrement | Sur le serveur |

**Recommandation : routage hors ligne sur le téléphone.** C'est ce qui rend la gratuité durable : le coût ne grandit pas avec le nombre d'utilisateurs.

## 6. Licences

- **ODbL (OSM)** : mention obligatoire « © contributeurs OpenStreetMap » ; si tu distribues une base dérivée modifiée, elle doit rester sous ODbL. Le code de l'app peut avoir la licence de ton choix.
- Préférer des briques **permissives** (MIT, BSD, Apache) : les bibliothèques GPL posent problème sur l'App Store.

## 7. Stores

- Google Play : 25 $ une fois. Apple : 99 $/an (exonération possible seulement pour les associations à but non lucratif *(à vérifier)*). F-Droid : gratuit, adapté à une app libre.
- iOS impose des justifications pour la localisation en arrière-plan ; c'est standard pour un GPS mais à soigner.

## 8. Contraintes légales en France

- **Avertisseurs de radars interdits** : ne pas afficher l'emplacement des radars, seulement des « zones de danger » si un jour on le souhaite.
- **Pas de signalement de contrôles de police** (les préfets peuvent interdire leur diffusion sur certaines zones, loi LOM).
- **RGPD** : garder la position sur le téléphone, pas de compte, pas de pistage. Une politique de confidentialité courte suffit alors.
- **Responsabilité** : avertissement clair « la signalisation prime sur le GPS ».

## 9. Risques principaux

1. **Données OSM incomplètes sur les routes express** (risque n°1). Une route rapide non marquée `motorroad=yes` pourrait être proposée à une VSP. Parades : pénaliser fortement les `trunk` à chaussées séparées et limitées à 90 km/h et plus, permettre aux utilisateurs de signaler une erreur, corriger directement dans OSM (ça profite à tous).
2. **Effort de développement du guidage mobile** (recalcul, voix, arrière-plan, économie de batterie). Réduit fortement par Ferrostar, mais reste le plus gros chantier.
3. **Taille des données hors ligne** et mise à jour régulière, à automatiser.
4. **Coût Apple annuel**, seul coût fixe incompressible si l'app est sur iPhone.
5. **Dépendance aux services gratuits** (géocodage IGN, tuiles OpenFreeMap) : faibles risques, mais prévoir un repli auto-hébergé.

## 10. Pile recommandée

OSM (Geofabrik France) → Valhalla, profil dérivé de `motor_scooter` à 45 km/h → tuiles de routage + PMTiles servies depuis Cloudflare R2 → app mobile avec MapLibre Native + Ferrostar → recherche d'adresses via l'API IGN/Géoplateforme.

## 11. Feuille de route recommandée (10/10/2026)

1. **Prototype de routage** sur une région (sans app) : Valhalla + profil VSP, une série de trajets tests passant près de voies rapides, mesure des itinéraires qui empruntent une route interdite. Valide le risque n°1 avant d'investir dans l'app.
2. **Base véhicules** (en parallèle, sans code) : tableur Marque / Modèle / Motorisation avec masse, puissance, énergie, réservoir ou batterie, consommation homologuée, type de prise.
3. **Android d'abord** (25 $ une fois, F-Droid possible), iOS ensuite, avec les SDK natifs MapLibre + Ferrostar.
4. **Dépôt GitHub** pour héberger le code et les données.
5. **Version 1** : carte, recherche d'adresse, itinéraire VSP, guidage vocal hors ligne.
6. **Version 2** : consommation par motorisation, puis stations et bornes sur le trajet.
