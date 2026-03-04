import pypsa
import pandas as pd
import numpy as np

import src._1_data_prep as dp
import src._2_power_flow_optimization as pfo
import src.config as cfg

def calculate_total_cost(network: pypsa.Network) -> float:
    """
    Calcule le bilan financier de la simulation : 
    1. + Revenu lié au groupe Business
    2. + Revenu lié au groupe Private
    3. + Revenu lié au groupe Ship
    4. - Coût lié au réseau (Grid)+

    
    :param network: Le réseau PyPSA optimisé.
    :return: Le coût total en euros.
    """
    # Coût du réseau (Grid)
    grid_cost = network.generators_t.p['grid'] * cfg.GRID_COST_PER_MW
    
    # Coût du solaire (Solar)
    solar_cost = network.generators_t.p['solar'] * cfg.SOLAR_LCOE_EUR_MWH
    
    # Coût de la batterie (si utilisée)
    battery_cost = 0
    if cfg.STORAGE_y_or_n:
        battery_cost = network.storage_units_t.p['battery'] * cfg.SHORE_POWER_COST_PER_MW
    
    # Coût total
    total_cost = grid_cost.sum() + solar_cost.sum() + battery_cost.sum()
    
    return total_cost