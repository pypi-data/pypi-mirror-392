import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from datetime import datetime


def generate_simulation(sim_number, months, spikes):
    # Generate monthly dates
    start_date = datetime(2000, 1, 1)
    dates = pd.date_range(start_date, periods=months, freq="MS")

    # Population (stable with minor noise)
    base_population = 100000 + sim_number * 5000
    population = base_population + np.random.normal(0, 500, months)

    # Temperature (stable with noise)
    base_temp = 25 + sim_number * 0.1
    temperature = base_temp + np.random.normal(0, 1, months)

    # Rainfall
    rainfall = np.random.normal(0, 3, months)  # mostly near 0

    # Choose spike positions
    spike_positions = np.linspace(0, months - 1, spikes + 2, dtype=int)[1:-1]
    spike_positions = [pos + random.randint(-2, 2) for pos in spike_positions]
    spike_positions = [max(0, min(months - 1, pos)) for pos in spike_positions]

    # Ensure at least one spike in last 10 months
    if not any(pos >= months - 10 for pos in spike_positions):
        spike_positions[-1] = random.randint(months - 10, months - 1)

    for pos in spike_positions:
        rainfall[pos] += 50 + np.random.normal(0, 5)

    # Disease cases correlated with rainfall (3-month lag)
    lag = 3
    cases = np.zeros(months)
    for t in range(lag, months):
        cases[t] = max(0, 0.5 * rainfall[t - lag] + np.random.normal(0, 2))

    # Create DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "population": population,
            "rainfall": rainfall,
            "temperature": temperature,
            "disease_cases": cases,
        }
    )

    return df


if __name__ == "__main__":
    simulations = {}
    for sim in range(1, 8):
        months = 80 + sim * 10  # sim1=90, sim2=100, ..., sim7=150
        spikes = sim + 8  # sim1=9, sim2=10, ..., sim7=15
        simulations[f"sim{sim}"] = generate_simulation(sim, months, spikes)

    # Plot each simulation
    for sim_name, df in simulations.items():
        plt.figure(figsize=(12, 5))
        plt.plot(df["date"], df["rainfall"], label="Rainfall (mm)", color="blue")
        plt.plot(df["date"], df["disease_cases"], label="Disease Cases", color="red")
        plt.title(f"{sim_name} - Rainfall vs Disease Cases")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()
        plt.tight_layout()
        plt.show()
