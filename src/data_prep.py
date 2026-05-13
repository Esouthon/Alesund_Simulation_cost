# src/data_prep.py
import glob
import os

import pandas as pd

import src.config as cfg


def load_and_prepare_data() -> pd.DataFrame:
    """Load all raw CSV files from DATA_PATH and merge them on the Date index.

    Each CSV must have a 'Date' column used as the time index.
    Files are discovered recursively one level below DATA_PATH
    (e.g. data/raw/price_EUR_MWh/price_EUR_MWh.csv).
    """
    all_files = glob.glob(os.path.join(cfg.DATA_PATH, "*", "*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No CSV files found under {cfg.DATA_PATH!r}")

    dfs = [pd.read_csv(f, index_col="Date", parse_dates=True) for f in all_files]
    return pd.concat(dfs, axis=1).sort_index()


def sort_ship_columns(
    df: pd.DataFrame,
    start_idx: int = 6,
    first_ship: int = 0,
    last_ship: int | None = None,
) -> pd.DataFrame:
    """Return df with ship columns sorted by total annual consumption (descending).

    Non-ship columns (indices 0 .. start_idx - 1) keep their original order.
    The optional [first_ship : last_ship] slice selects a subset of ships after
    sorting, which is useful to focus on the largest consumers.

    Parameters
    ----------
    df         : Raw merged DataFrame from load_and_prepare_data.
    start_idx  : Column index at which ship data begins.
    first_ship : First ship to keep (0-based, after sorting).
    last_ship  : One past the last ship to keep (None = keep all).
    """
    base_cols = df.columns[:start_idx]
    ship_cols = df.columns[start_idx:]
    sorted_ships = df[ship_cols].sum().sort_values(ascending=False).index
    if last_ship is not None or first_ship != 0:
        sorted_ships = sorted_ships[first_ship:last_ship]
    return df[list(base_cols) + list(sorted_ships)]
