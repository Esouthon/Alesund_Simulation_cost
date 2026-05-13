import src.config as cfg
import src.data_prep as dp
import src.power_flow as pf


def main():
    print("=" * 60)
    print("  Alesund Port Microgrid — PyPSA Single-Run Optimisation")
    print("=" * 60)

    print("[1/3] Loading and preparing demand time series...")
    df = dp.sort_ship_columns(dp.load_and_prepare_data())
    print(f"      → {len(df)} hourly snapshots  |  {df.shape[1]} columns")

    print(f"[2/3] Building PyPSA network "
          f"(PV = {cfg.SOLAR_CAPACITY_MW} MW, battery enabled)...")
    network = pf.create_pypsa_network(df, cfg.SOLAR_CAPACITY_MW, Battery=True)

    print("[3/3] Running linear optimisation...")
    status, condition = network.optimize()
    print(f"      → {status} ({condition})")

    if status == "ok":
        e_imp = float(network.generators_t.p["grid"].clip(lower=0).sum())
        e_pv  = float(network.generators_t.p["solar"].sum())
        e_dem = float(network.loads_t.p.sum().sum())
        print()
        print(f"  Total demand    : {e_dem:>10,.1f} MWh/yr")
        print(f"  Grid imports    : {e_imp:>10,.1f} MWh/yr")
        print(f"  PV generation   : {e_pv:>10,.1f} MWh/yr")
        print(f"  RE coverage     : {(e_dem - e_imp) / e_dem * 100:>9.1f} %")
        print(f"  Total OPEX      : {network.objective / 1e6:>10.3f} M€/yr")


if __name__ == "__main__":
    main()
