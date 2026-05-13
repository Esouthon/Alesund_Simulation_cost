# Alesund Port Microgrid — Shore Power Optimisation with PyPSA

This project models and optimises the energy flows of a port that provides
shore power to berthed cruise ships. Using [PyPSA](https://pypsa.org/), it
simulates the integration of solar PV, battery storage, and grid purchases to
meet the electricity demand of port infrastructure and visiting vessels.

The core analysis is a **bi-objective Pareto sweep** over PV capacity and
battery size that trades off total annualised cost against renewable energy
coverage.

## Project structure

```
.
├── data/
│   └── raw/                      # Input time series (one sub-folder per variable)
│       ├── price_EUR_MWh/
│       ├── radiation_solaire_factor/
│       ├── business_MWh/
│       ├── private_MWh/
│       ├── CO2_g_MWh/
│       ├── t2m_C/
│       └── ship/                 # One CSV per vessel
├── src/
│   ├── config.py                 # All techno-economic parameters
│   ├── data_prep.py              # Data loading and pre-processing
│   └── power_flow.py             # PyPSA network construction
├── pareto_analysis.ipynb         # Main analysis — Pareto front generation & plots
├── main.py                       # Quick single-run entry point
└── requirements.txt
```

## Scenarios

| Scenario | PV capacity | Battery capacity |
|---|---|---|
| **S0 — Reference** | 0 MW | 0 MWh |
| **S1 — PV only** | 0 → 100 MW | 0 MWh |
| **S2 — PV + Battery** | 0 → 100 MW | 0 → 15 MWh |

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

**Single optimisation run** (configuration from `src/config.py`):

```bash
python main.py
```

**Full Pareto analysis** (generates all figures and CSV outputs):

```bash
jupyter notebook pareto_analysis.ipynb
```

## Key outputs

| File | Description |
|---|---|
| `pareto_all_scenarios.csv` | Full grid-search results (all LP solutions) |
| `pareto_key_points.csv` | KPIs of the four canonical Pareto points |
| `pareto_summary.csv` | Cost-optimal configuration for each scenario |

> Output files are not tracked by git — run the notebook to regenerate them.
