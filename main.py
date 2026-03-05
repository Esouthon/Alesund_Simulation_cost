import src.config as cfg
import src._1_data_prep as dp
import src._2_power_flow_optimization as pfo
from src._3_overall_cost import generer_bilan_financier
import pypsa

def main():
    print("="*40)
    print(" Lancement de la simulation PyPSA")
    print("="*40)
    
    # 1. Préparation des données
    print("[1/4] Chargement et préparation des données...")
    df = dp.sort_ship_columns(dp.load_and_prepare_data())
    
    # 2. Création du réseau PyPSA
    print(f"[2/4] Création du réseau (Solaire : {cfg.SOLAR_CAPACITY_MW} MW, Batterie : Oui)...")
    network = pfo.create_pypsa_network(df, cfg.SOLAR_CAPACITY_MW, True)
    
    # 3. Lancement de l'optimisation
    print("[3/4] Optimisation du réseau en cours (cela peut prendre un moment)...")
    status, condition = network.optimize()
    print(f"      -> Statut de l'optimisation : {status} ({condition})")
    
    # 4. Génération du bilan financier
    print("[4/4] Génération du bilan financier...")
    # On passe cfg en paramètre pour accéder au tarif de revente (SHORE_POWER_COST_PER_MW)
    resultats_financiers = generer_bilan_financier(network)
    
    print("\n--- Fin de l'exécution ---")

if __name__ == "__main__":
    main()