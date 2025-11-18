from mestDS.classes.Simulation import Simulations

sims = Simulations("scripts/chakri_sims.yaml")
sims.simulate()
sims.plot_data()
