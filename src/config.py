# src/config.py
# Configuration parameters for the Alesund port microgrid simulation.

# ─────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────
DATA_PATH = "data/raw"

# ─────────────────────────────────────────────────────────
#  Financial parameters
# ─────────────────────────────────────────────────────────
SHORE_POWER_TARIFF_EUR_MWH = 300    # Shore-power selling price charged to ships (€/MWh)
GRID_TAX_EUR_MWH = 100              # Network tax applied on grid electricity purchases (€/MWh)
DISCOUNT_RATE = 0.05                # Weighted average cost of capital

# ─────────────────────────────────────────────────────────
#  Solar PV
# ─────────────────────────────────────────────────────────
SOLAR_CAPACITY_MW = 10              # Default installed capacity (MW)
EFFICIENCY_LINK_SOLAR = 0.9        # DC/AC + cabling efficiency
SOLAR_CO2_EMISSION_G_MWH = 15_000  # Lifecycle CO₂ intensity (gCO₂/MWh)
SOLAR_CAPEX_MW = 800_000           # Capital cost (€/MW)
SOLAR_OPEX_FIXED_MW = 10_000       # Fixed O&M (€/MW/year)
SOLAR_OPEX_VAR_MWH = 0.01          # Variable O&M (€/MWh)
SOLAR_LIFETIME = 40                # Technical lifetime (years)

# ─────────────────────────────────────────────────────────
#  Battery energy storage
# ─────────────────────────────────────────────────────────
STORAGE_CAPACITY_MW = 10           # Default power rating (MW)
STORAGE_EFFICIENCY_STORE = 0.9     # Charging efficiency
STORAGE_EFFICIENCY_DISPATCH = 0.85 # Discharging efficiency
BATTERY_CAPEX_MWH = 1_500_000     # Capital cost (€/MWh)
BATTERY_OPEX_FIXED_MWH = 20_000   # Fixed O&M (€/MWh/year)
BATTERY_OPEX_VAR_MWH = 4.0        # Cycling / degradation cost (€/MWh)
BATTERY_LIFETIME = 15              # Technical lifetime (years)

# ─────────────────────────────────────────────────────────
#  Shore-power quayside link
# ─────────────────────────────────────────────────────────
EFFICIENCY_LINK_SHIP = 0.9         # Quayside converter efficiency


# ─────────────────────────────────────────────────────────
#  Derived costs (computed once at import time)
# ─────────────────────────────────────────────────────────
def _annualised_cost(capex: float, fixed_opex: float,
                     discount_rate: float, lifetime: int) -> float:
    """Capital-recovery factor × CAPEX + fixed O&M (€ per unit per year)."""
    crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
    return capex * crf + fixed_opex


SOLAR_ANNUALISED_COST = _annualised_cost(
    SOLAR_CAPEX_MW, SOLAR_OPEX_FIXED_MW, DISCOUNT_RATE, SOLAR_LIFETIME
)

BATTERY_ANNUALISED_COST = _annualised_cost(
    BATTERY_CAPEX_MWH, BATTERY_OPEX_FIXED_MWH, DISCOUNT_RATE, BATTERY_LIFETIME
)
