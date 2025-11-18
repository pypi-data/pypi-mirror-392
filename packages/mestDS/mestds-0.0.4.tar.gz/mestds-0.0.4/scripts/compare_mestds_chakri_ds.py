import os
import sys
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from mestDS.classes.Simulation import Simulations


def plot(mestds_dc, chs_dc, title):
    plt.figure(figsize=(10, 6))
    plt.plot(mestds_dc, label="mestDS Disease Cases")
    plt.plot(
        chs_dc,
        label="Climate Health Simulations Disease Cases",
    )
    plt.xlabel("Time")
    plt.ylabel("Disease Cases")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{title}.png")
    plt.show()


ch_sim = Simulations("scripts/climate_health_simulation_recreation.yaml")
ch_sim.simulate()
ch_sim.convert_to_csvs("testing_minimalist_multiregion/")


options = ["non_", ""]
for x in options:
    chs = pd.read_csv(f"datasets/chakri_climate_dependent_{x}autoregressive.csv")
    mestds = next(
        sim
        for sim in ch_sim.simulations
        if sim.simulation_name
        == f"config_climate_and_season_dependent_{x}autoregressive"
    )
    chs_disease_cases = chs["disease_cases"]
    mestds_disease_cases = mestds.data["Finnmark"]["disease_cases"][2:]
    plot(
        mestds_disease_cases,
        chs_disease_cases,
        f"mestDS vs. climate_health_simulations - {x.replace('_','')} autoregressive",
    )
