import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from mestDS.mestDS import mestDS

mestds_1 = mestDS("dsl_v3/random_rain.yaml")

sims = mestds_1.simulate()
# mestds_1.plot_data()
mestds_1.evaluate(sims, report_path="reports/random/")
