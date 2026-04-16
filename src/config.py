# src/config.py

# Path to the data directory
DATA_PATH = 'data/raw'

# Financial Rules 

SHORE_POWER_COST_PER_MW = 333 # €/MWh
TAX_PRICE=60 #€/MWh
MAXIMUM_ELEC_PRICE=150 #€
DISCOUNT_RATE = 0.06

# Grid Parameters
    ## Storage/Battery
STORAGE_y_or_n=False
STORAGE_CAPACITY_MWH = 8 # MWh
STORAGE_POWER_MW = 2 # MW
STORAGE_EFFICIENCY_STORE = 0.9
STORAGE_EFFICIENCY_DISPATCH = 0.85
STORAGE_EFFICIENCY_DC_TO_AC = 0.9
SOC_t_0 = 0.5 # State of Charge initial (50% de la capacité)

BATTERY_CAPEX_MWH = 300000 #€/MWh
BATTERY_OPEX_FIXED_MWH = 6000  # €/MWh/an
BATTERY_OPEX_VAR_MWH = 4.0       # €/MWh (Coût de cyclage/dégradation)
BATTERY_LIFETIME = 15            # Années

STORAGE_LCOS_EUR_MWH = 80 # €/MWh


    ## Solar
SOLAR_CAPACITY_MW = 10 #MW
EFFICIENCY_LINK_SOLAR = 0.9
SOLAR_CO2_EMISSION_g_MWH = 15e3  # gCO2 / MW
SOLAR_CAPEX_MW= 800_000 # €/MW
SOLAR_OPEX_FIXED_MW=12000 # €/MW/an
SOLAR_OPEX_VAR_MWH = 0.01 # €/MWh
SOLAR_LIFETIME = 25 # Années

    ## Ship
EFFICIENCY_LINK_SHIP = 0.9


def calculate_annualised_cost(capex: float, fixed_opex: float, discount_rate: float, lifetime: int) -> float:
    """
    Calcule le coût annualisé (capital_cost) pour PyPSA.
    """
    # Facteur de recouvrement du capital (CRF)
    crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
    return (capex * crf) + fixed_opex

SOLAR_ANNUALISED_COST = calculate_annualised_cost(
    SOLAR_CAPEX_MW, SOLAR_OPEX_FIXED_MW, DISCOUNT_RATE, SOLAR_LIFETIME
)

BATTERY_ANNUALISED_COST = calculate_annualised_cost(
    BATTERY_CAPEX_MWH, BATTERY_OPEX_FIXED_MWH, DISCOUNT_RATE, BATTERY_LIFETIME
)


