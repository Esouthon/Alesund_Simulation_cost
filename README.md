# Optimisation de Micro-réseau Portuaire (Shore Power) avec PyPSA

Ce projet modélise et optimise les flux d'énergie d'un port proposant une alimentation électrique à quai (Shore Power) pour les navires. En utilisant la bibliothèque d'analyse de systèmes électriques PyPSA, le code simule l'intégration de panneaux solaires, de batteries de stockage et l'achat d'électricité sur le réseau pour répondre à la demande énergétique des infrastructures portuaires et des navires accostés.

##  Architecture du Projet

Le projet est divisé en quatre modules principaux situés dans le dossier source :

* **`config.py` (Configuration et Paramètres)**
    * Définit les coûts (CAPEX, OPEX, prix de l'électricité, tarif de revente aux navires).
    * Configure les paramètres techniques des équipements (capacités solaires et batteries, rendements de conversion).

* **`_1_data_prep.py` (Préparation des données)**
    * Charge les données brutes au format CSV depuis le répertoire `data/raw/`.
    * Concatène les séries temporelles en les alignant sur un index chronologique (Date).
    * Propose une fonction `sort_ship_columns` pour trier les navires par volume de consommation décroissant et tronquer la liste si besoin (pour se concentrer sur les plus gros consommateurs).

* **`_2_power_flow_optimization.py` (Modélisation du Réseau)**
    * Construit le réseau d'énergie à l'aide de PyPSA.
    * **Buses** : Crée des nœuds de connexion (bus principal, bus solaire, bus navires).
    * **Générateurs** : Ajoute le réseau électrique principal (avec des coûts marginaux dynamiques incluant les taxes) et la production solaire locale.
    * **Charges** : Intègre les consommations fixes (Business, Private) et génère dynamiquement une charge individuelle pour chaque navire présent dans les données.
    * **Stockage (Optionnel)** : Permet d'intégrer une batterie de stockage avec ses cycles de charge/décharge liés au solaire et au réseau principal.

* **`_3_overall_cost.py` (Bilan Financier)**
    * Analyse les résultats post-optimisation de PyPSA.
    * Calcule l'ensemble des dépenses : factures énergétiques (Business, Private, Navires) et les coûts d'infrastructure (CAPEX/OPEX du solaire et du stockage).
    * Calcule les revenus générés par la revente d'énergie aux navires au tarif défini.
    * Génère et affiche un bilan financier complet (Profit ou Déficit) pour la municipalité.

##  Prérequis et Installation

Assurez-vous d'avoir les bibliothèques Python suivantes installées pour exécuter le projet :

* `pandas` (pour la manipulation des séries temporelles)
* `numpy` (pour les calculs numériques)
* `pypsa` (pour l'optimisation des flux de puissance)

##  Fonctionnement du Pipeline

1.  **Ingestion** : Les données météorologiques, les prix de marché et les profils de consommation des navires sont chargés et fusionnés.
2.  **Modélisation** : Le réseau est modélisé sous forme de graphe (nœuds et liens) avec des contraintes physiques (capacités, rendements) et économiques.
3.  **Optimisation** : PyPSA résout le flux de puissance optimal sur l'année pour minimiser les coûts globaux de fourniture d'énergie.
4.  **Évaluation** : Le bilan financier agrège les résultats pour déterminer la rentabilité globale des investissements (Solaire + Batterie) et du service de Shore Power.