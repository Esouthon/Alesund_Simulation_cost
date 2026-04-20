import pypsa
import src.config as cfg
import pandas as pd
import numpy as np



def create_pypsa_network(df: pd.DataFrame,PV_nominal_capacity: float, Battery: bool, index_ship=6) -> pypsa.Network:
    """
    Construit et optimise le réseau PyPSA pour le microgrid du port.
    
    :param df: DataFrame contenant les séries temporelles (météo, prix, consos).
    :param PV_nominal: Puissance nominale des panneaux solaires.
    :return: Le réseau PyPSA .
    """
    network = pypsa.Network()
    network.set_snapshots(df.index)

    network.add(
    "Carrier",
    ["Grid", "Solar", "Battery","Business", "Private", "Ship"])
    # ==================== 1. BUSES ====================
    # Le bus principal du port
    network.add("Bus", "bus_main")
    network.add("Bus", "bus_ship")
    network.add("Bus", "bus_solar")

    # ==================== 2. LINKS ====================
    # Convertisseur de quai (Shore Power) avec 10% de pertes
    network.add("Link", "link_shore_power",
                bus0="bus_main",
                bus1="bus_ship",
                p_nom=50,      #
                efficiency=cfg.EFFICIENCY_LINK_SHIP) # Rendement de 90% vers les navires
    
    network.add("Link", "link_solar_main",
            bus0="bus_solar",
            bus1="bus_main",
            p_nom=1e6,      
            efficiency=cfg.EFFICIENCY_LINK_SOLAR) # Rendement de 90% du solaire vers le bus principal

    # ==================== 3. GENERATORS ====================
    # Générateur Réseau (Achat d'électricité)
    network.add("Generator", "grid",
                bus="bus_main",
                p_nom=1e6,
                marginal_cost=np.minimum(df['price_EUR_MWh'] + cfg.TAX_PRICE, cfg.MAXIMUM_ELEC_PRICE),
                carrier='Grid')
    
    # Générateur Solaire (Production locale)
    network.add("Generator", "solar",
                bus="bus_solar",
                p_nom=cfg.SOLAR_CAPACITY_MW, # Ou p_nom_extendable=True si tu veux optimiser la taille
                p_max_pu=df['radiation_solaire_factor'],
                capital_cost=cfg.SOLAR_ANNUALISED_COST,
                marginal_cost=cfg.SOLAR_OPEX_VAR_MWH,
                carrier='Solar')

    # ==================== 4. LOADS ====================
    # Charges fixes (hors navires)
    network.add("Load", "private_load", bus="bus_main", p_set=df['private_MWh'], carrier="Private")
    network.add("Load", "business_load", bus="bus_main", p_set=df['business_MWh'], carrier="Business")

    # --- DYNAMIQUE : Charges séparées pour chaque navire ---
    for navire in df.iloc[:,index_ship:].columns:
        network.add("Load", 
                    f"load_ship_{navire}", 
                    bus="bus_ship", 
                    p_set=df[navire],
                    carrier="Ship"
                    )
    # Ajout de la batterie
    if (Battery):
        network.add("Bus", "bus_battery")
        # Lien grid
            # Décharge
        network.add("Link", "link_battery_to_main",
                bus0="bus_battery",
                bus1="bus_main",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) 
            # Charge réseau
        network.add("Link", "link_main_to_battery",
                bus0="bus_main",
                bus1="bus_battery",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) 
        #Charge Solaire
        network.add("Link", "link_solar_to_battery",
                bus0="bus_solar",
                bus1="bus_battery",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) # On charge facilement le solaire avec la batterie
        
        network.add("StorageUnit", "battery",
                    bus="bus_battery",
                    p_nom=cfg.STORAGE_CAPACITY_MWH, # Ou p_nom_extendable=True
                    efficiency_store=cfg.STORAGE_EFFICIENCY_STORE,
                    efficiency_dispatch=cfg.STORAGE_EFFICIENCY_DISPATCH,
                    capital_cost=cfg.BATTERY_ANNUALISED_COST,
                    marginal_cost=cfg.BATTERY_OPEX_VAR_MWH,
                    state_of_charge_initial=cfg.SOC_t_0,
                    carrier='Battery')
    return network


import pypsa
import src.config as cfg
import pandas as pd
import numpy as np



def create_pypsa_network_opti(df: pd.DataFrame,PV_nominal_capacity: float, Battery: bool, index_ship=6) -> pypsa.Network:
    """
    Construit et optimise le réseau PyPSA pour le microgrid du port.
    
    :param df: DataFrame contenant les séries temporelles (météo, prix, consos).
    :param PV_nominal: Puissance nominale des panneaux solaires.
    :return: Le réseau PyPSA .
    """
    network = pypsa.Network()
    network.set_snapshots(df.index)

    network.add(
    "Carrier",
    ["Grid", "Solar", "Battery","Business", "Private", "Ship"])
    # ==================== 1. BUSES ====================
    # Le bus principal du port
    network.add("Bus", "bus_main")
    network.add("Bus", "bus_ship")
    network.add("Bus", "bus_solar")

    # ==================== 2. LINKS ====================
    # Convertisseur de quai (Shore Power) avec 10% de pertes
    network.add("Link", "link_shore_power",
                bus0="bus_main",
                bus1="bus_ship",
                p_nom=50,      #
                efficiency=cfg.EFFICIENCY_LINK_SHIP) # Rendement de 90% vers les navires
    
    network.add("Link", "link_solar_main",
            bus0="bus_solar",
            bus1="bus_main",
            p_nom=1e6,      
            efficiency=cfg.EFFICIENCY_LINK_SOLAR) # Rendement de 90% du solaire vers le bus principal

    # ==================== 3. GENERATORS ====================
    # Générateur Réseau (Achat d'électricité)
    network.add("Generator", "grid",
                bus="bus_main",
                p_nom=1e6,
                marginal_cost=np.minimum(df['price_EUR_MWh'] + cfg.TAX_PRICE, cfg.MAXIMUM_ELEC_PRICE),
                carrier='Grid')
    
    # Générateur Solaire (Production locale)
    network.add("Generator", "solar",
                bus="bus_solar",
                p_nom_extendable=True, #cfg.SOLAR_CAPACITY_MW, # Ou p_nom_extendable=True si tu veux optimiser la taille
                p_max_pu=df['radiation_solaire_factor'],
                capital_cost=cfg.SOLAR_ANNUALISED_COST,
                marginal_cost=cfg.SOLAR_OPEX_VAR_MWH,
                carrier='Solar')

    # ==================== 4. LOADS ====================
    # Charges fixes (hors navires)
    network.add("Load", "private_load", bus="bus_main", p_set=df['private_MWh'], carrier="Private")
    network.add("Load", "business_load", bus="bus_main", p_set=df['business_MWh'], carrier="Business")

    # --- DYNAMIQUE : Charges séparées pour chaque navire ---
    for navire in df.iloc[:,index_ship:].columns:
        network.add("Load", 
                    f"load_ship_{navire}", 
                    bus="bus_ship", 
                    p_set=df[navire],
                    carrier="Ship"
                    )
    # Ajout de la batterie
    if (Battery):
        network.add("Bus", "bus_battery")
        # Lien grid
            # Décharge
        network.add("Link", "link_battery_to_main",
                bus0="bus_battery",
                bus1="bus_main",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) 
            # Charge réseau
        network.add("Link", "link_main_to_battery",
                bus0="bus_main",
                bus1="bus_battery",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) 
        #Charge Solaire
        network.add("Link", "link_solar_to_battery",
                bus0="bus_solar",
                bus1="bus_battery",
                p_nom=1e6,      # Capacité "infinie"
                efficiency=1) # On charge facilement le solaire avec la batterie
        
        network.add("StorageUnit", "battery",
                    bus="bus_battery",
                    p_nom_extendable=True,
                    #p_nom=cfg.STORAGE_CAPACITY_MWH, # Ou p_nom_extendable=True
                    efficiency_store=cfg.STORAGE_EFFICIENCY_STORE,
                    efficiency_dispatch=cfg.STORAGE_EFFICIENCY_DISPATCH,
                    capital_cost=cfg.BATTERY_ANNUALISED_COST,
                    marginal_cost=cfg.BATTERY_OPEX_VAR_MWH,
                    state_of_charge_initial=cfg.SOC_t_0,
                    carrier='Battery')
    return network
