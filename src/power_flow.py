# src/power_flow.py
import pandas as pd
import pypsa

import src.config as cfg


def create_pypsa_network(
    df: pd.DataFrame,
    PV_nominal_capacity: float,
    Battery: bool,
    index_ship: int = 6,
) -> pypsa.Network:
    """Build a PyPSA LP network for the port microgrid.

    Parameters
    ----------
    df                  : Hourly time series (weather, prices, loads).
    PV_nominal_capacity : Initial PV installed capacity (MW); can be
                          overwritten before calling optimize().
    Battery             : Whether to include a battery storage unit.
    index_ship          : Column index at which ship loads begin in df.
    """
    network = pypsa.Network()
    network.set_snapshots(df.index)

    network.add("Carrier", ["Grid", "Solar", "Battery", "Business", "Private", "Ship"])

    # ── Buses ──────────────────────────────────────────────────────────────
    network.add("Bus", "bus_main")
    network.add("Bus", "bus_ship")
    network.add("Bus", "bus_solar")

    # ── Links ──────────────────────────────────────────────────────────────
    network.add("Link", "link_shore_power",
                bus0="bus_main", bus1="bus_ship",
                p_nom=1e6,
                efficiency=cfg.EFFICIENCY_LINK_SHIP)

    network.add("Link", "link_solar_main",
                bus0="bus_solar", bus1="bus_main",
                p_nom=1e6,
                efficiency=cfg.EFFICIENCY_LINK_SOLAR)

    # ── Generators ─────────────────────────────────────────────────────────
    network.add("Generator", "grid",
                bus="bus_main",
                p_nom=1e6,
                p_min_pu=0,
                p_max_pu=1,
                marginal_cost=df["price_EUR_MWh"] + cfg.GRID_TAX_EUR_MWH,
                carrier="Grid")

    network.add("Generator", "solar",
                bus="bus_solar",
                p_nom=cfg.SOLAR_CAPACITY_MW,
                p_max_pu=df["radiation_solaire_factor"],
                capital_cost=cfg.SOLAR_ANNUALISED_COST,
                marginal_cost=cfg.SOLAR_OPEX_VAR_MWH,
                carrier="Solar")

    # ── Loads ──────────────────────────────────────────────────────────────
    network.add("Load", "private_load", bus="bus_main",
                p_set=df["private_MWh"], carrier="Private")
    network.add("Load", "business_load", bus="bus_main",
                p_set=df["business_MWh"], carrier="Business")

    for ship in df.iloc[:, index_ship:].columns:
        network.add("Load", f"load_ship_{ship}",
                    bus="bus_ship", p_set=df[ship], carrier="Ship")

    # ── Battery (optional) ─────────────────────────────────────────────────
    if Battery:
        network.add("Bus", "bus_battery")
        network.add("Link", "link_battery_to_main",
                    bus0="bus_battery", bus1="bus_main", p_nom=1e6, efficiency=1)
        network.add("Link", "link_main_to_battery",
                    bus0="bus_main", bus1="bus_battery", p_nom=1e6, efficiency=1)
        network.add("Link", "link_solar_to_battery",
                    bus0="bus_solar", bus1="bus_battery", p_nom=1e6, efficiency=1)
        network.add("StorageUnit", "battery",
                    bus="bus_battery",
                    p_nom=cfg.STORAGE_CAPACITY_MW,
                    max_hours=4,
                    efficiency_store=cfg.STORAGE_EFFICIENCY_STORE,
                    efficiency_dispatch=cfg.STORAGE_EFFICIENCY_DISPATCH,
                    capital_cost=cfg.BATTERY_ANNUALISED_COST,
                    marginal_cost=cfg.BATTERY_OPEX_VAR_MWH,
                    state_of_charge_initial=0,
                    carrier="Battery")

    return network


def create_pypsa_network_extendable(
    df: pd.DataFrame,
    Battery: bool,
    index_ship: int = 6,
) -> pypsa.Network:
    """Like create_pypsa_network but with extendable PV and battery capacities
    and a grid-export generator.

    Intended for a single LP that jointly optimises installed capacity.
    """
    network = pypsa.Network()
    network.set_snapshots(df.index)

    network.add("Carrier", ["Grid", "Solar", "Battery", "Business", "Private", "Ship"])

    network.add("Bus", "bus_main")
    network.add("Bus", "bus_ship")
    network.add("Bus", "bus_solar")

    network.add("Link", "link_shore_power",
                bus0="bus_main", bus1="bus_ship",
                p_nom=1e6, efficiency=cfg.EFFICIENCY_LINK_SHIP)
    network.add("Link", "link_solar_main",
                bus0="bus_solar", bus1="bus_main",
                p_nom=1e6, efficiency=cfg.EFFICIENCY_LINK_SOLAR)

    network.add("Generator", "grid_import",
                bus="bus_main", p_nom=1e6,
                p_min_pu=0, p_max_pu=1,
                marginal_cost=df["price_EUR_MWh"] + cfg.GRID_TAX_EUR_MWH,
                carrier="Grid")

    network.add("Generator", "grid_export",
                bus="bus_main", p_nom=1e6,
                p_min_pu=-1, p_max_pu=0,
                marginal_cost=df["price_EUR_MWh"],
                carrier="Grid")

    network.add("Generator", "solar",
                bus="bus_solar",
                p_nom_extendable=True,
                p_max_pu=df["radiation_solaire_factor"],
                capital_cost=cfg.SOLAR_ANNUALISED_COST,
                marginal_cost=cfg.SOLAR_OPEX_VAR_MWH,
                carrier="Solar")

    network.add("Load", "private_load", bus="bus_main",
                p_set=df["private_MWh"], carrier="Private")
    network.add("Load", "business_load", bus="bus_main",
                p_set=df["business_MWh"], carrier="Business")

    for ship in df.iloc[:, index_ship:].columns:
        network.add("Load", f"load_ship_{ship}",
                    bus="bus_ship", p_set=df[ship], carrier="Ship")

    if Battery:
        network.add("Bus", "bus_battery")
        network.add("Link", "link_battery_to_main",
                    bus0="bus_battery", bus1="bus_main", p_nom=1e6, efficiency=1)
        network.add("Link", "link_main_to_battery",
                    bus0="bus_main", bus1="bus_battery", p_nom=1e6, efficiency=1)
        network.add("Link", "link_solar_to_battery",
                    bus0="bus_solar", bus1="bus_battery", p_nom=1e6, efficiency=1)
        network.add("StorageUnit", "battery",
                    bus="bus_battery",
                    p_nom_extendable=True,
                    efficiency_store=cfg.STORAGE_EFFICIENCY_STORE,
                    efficiency_dispatch=cfg.STORAGE_EFFICIENCY_DISPATCH,
                    capital_cost=cfg.BATTERY_ANNUALISED_COST,
                    marginal_cost=cfg.BATTERY_OPEX_VAR_MWH,
                    state_of_charge_initial=0,
                    carrier="Battery")

    return network
