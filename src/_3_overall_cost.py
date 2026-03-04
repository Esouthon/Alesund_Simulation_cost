import pypsa
import pandas as pd
import numpy as np

import src._1_data_prep as dp
import src._2_power_flow_optimization as pfo
import src.config as cfg


def generer_bilan_financier(network):
    # 1. Récupération des statistiques globales post-optimisation
    stats = network.statistics()
    
    # --------------------------------------------------------
    # DÉPENSES (Facture énergétique & Coûts d'infrastructure)
    # --------------------------------------------------------
    
    # A. Ma facture énergétique (Load)
    # stats.loc["Load"] permet de cibler uniquement les charges.
    # On prend la colonne "Revenue" (négative) et on la passe en positif pour avoir la dépense.
    if "Load" in stats.index.get_level_values(0):
        depenses_loads = -stats.loc["Load", "Revenue"]
        
        # Détail par usage (le .get() évite une erreur si l'un d'eux n'est pas dans le réseau)
        depense_business = depenses_loads.get("Business", 0)
        depense_private = depenses_loads.get("Private", 0)
        depense_ship_achat = depenses_loads.get("Ship", 0)
        
        # Total de la facture énergétique du réseau
        depense_energie = depenses_loads.sum()
    else:
        depense_business = depense_private = depense_ship_achat = depense_energie = 0

    # B. Dépenses CAPEX et OPEX Solaire
    if ("Generator", "Solar") in stats.index:
        depense_solaire = (stats.loc[("Generator", "Solar"), "Capital Expenditure"] + 
                           stats.loc[("Generator", "Solar"), "Operational Expenditure"])
    else:
        depense_solaire = 0

    # C. Dépenses CAPEX et OPEX Stockage (Batterie)
    if ("StorageUnit", "Battery") in stats.index:
        depense_stockage = (stats.loc[("StorageUnit", "Battery"), "Capital Expenditure"] + 
                            stats.loc[("StorageUnit", "Battery"), "Operational Expenditure"])
    else:
        depense_stockage = 0

    # Total de toutes les dépenses de la municipalité
    total_depenses = depense_energie + depense_solaire + depense_stockage

    # --------------------------------------------------------
    # REVENUS (Vente de l'énergie aux navires)
    # --------------------------------------------------------
    
    # On récupère dynamiquement tous les navires via leur "carrier"
    index_of_ship = network.loads[network.loads.carrier == 'Ship'].index
    
    if len(index_of_ship) > 0:
        # Volume total d'énergie consommé par l'ensemble des navires (MWh)
        energie_totale_navire = network.loads_t.p[index_of_ship].sum().sum()
        # Revenu généré par la revente (Tarif SP * Volume)
        revenu_sp = cfg.SHORE_POWER_COST_PER_MW * energie_totale_navire
    else:
        revenu_sp = 0

    # --------------------------------------------------------
    # BILAN ANNUEL
    # --------------------------------------------------------
    bilan = revenu_sp - total_depenses

    # --------------------------------------------------------
    # AFFICHAGE
    # --------------------------------------------------------
    print("="*40)
    print(" BILAN FINANCIER ANNUEL DE LA MUNICIPALITÉ ")
    print("="*40)
    print("\n[DÉPENSES]")
    print(f"  Facture énergétique (Business) : {depense_business:,.2f} €")
    print(f"  Facture énergétique (Private)  : {depense_private:,.2f} €")
    print(f"  Facture énergétique (Ship)     : {depense_ship_achat:,.2f} €")
    print(f"  CAPEX + OPEX Solaire           : {depense_solaire:,.2f} €")
    print(f"  CAPEX + OPEX Batterie          : {depense_stockage:,.2f} €")
    print("-" * 40)
    print(f"  TOTAL DÉPENSES                 : {total_depenses:,.2f} €")
    
    print("\n[REVENUS]")
    print(f"  Vente énergie navires (SP)     : {revenu_sp:,.2f} €")
    print("-" * 40)
    
    print("\n[BILAN]")
    if bilan >= 0:
        print(f"  PROFIT                         : +{bilan:,.2f} €")
    else:
        print(f"  DÉFICIT                        : {bilan:,.2f} €")
    print("="*40)
    
    return {
        "depenses_energie": depense_energie,
        "depenses_solaire": depense_solaire,
        "depenses_stockage": depense_stockage,
        "total_depenses": total_depenses,
        "revenu_sp": revenu_sp,
        "bilan": bilan
    }